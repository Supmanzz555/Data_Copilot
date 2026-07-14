from collections import defaultdict, deque
import time

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from groq import Groq
from sqlalchemy import text
from app.mcp_tools import sql_query, kb_search, kpi_top_root_causes
from app.config import settings
from app.database import engine as sync_engine
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY, ACTIVE_REQUESTS, ERROR_COUNT
from pydantic import BaseModel
import asyncio
import json
import logging
import re
import sqlparse
from app.guardrails import is_read_query

logger = logging.getLogger(__name__)
router = APIRouter()
client = Groq(api_key=settings.GROQ_API_KEY)
# define tools
TOOLS = {
    "sql.query": sql_query,
    "kb.search": kb_search,
    "kpi.top_root_causes": kpi_top_root_causes
}

_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 10
_request_log: dict[str, deque[float]] = defaultdict(deque)

class AskPayload(BaseModel):
    question: str
    history: list[dict] = []

async def _groq_chat_create_with_backoff(**kwargs):
    """
    Groq can rate-limit on TPM. This retries a few times on 429 with short backoff.
    """
    last_err: Exception | None = None
    for attempt in range(4):
        try:
            return await asyncio.to_thread(client.chat.completions.create, **kwargs)
        except Exception as e:
            last_err = e
            msg = str(e)
            if "Error code: 429" in msg or "rate_limit" in msg.lower():
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            raise
    raise last_err or RuntimeError("Groq request failed after retries")

def _strip_as_in_group_by(m: re.Match) -> str:
    clause = m.group(1)
    clause = re.sub(r"\bAS\s+\w+\s*,?\s*", ", ", clause)
    clause = re.sub(r",\s*,", ",", clause).strip().rstrip(",")
    return f"GROUP BY {clause}"


def _sanitize_generated_sql(sql: str) -> str:
    """
    Patch common LLM SQL mistakes for this repo's schema without changing intent.
    Keep this conservative: only fix known, safe patterns.
    """
    fixed = sql

    # GROUP BY cannot contain "AS alias" — strip all occurrences
    fixed = re.sub(r"\bGROUP\s+BY\s+(.+?)(?=\s+(?:ORDER|LIMIT|HAVING|;|$)|$)", _strip_as_in_group_by, fixed, flags=re.IGNORECASE | re.DOTALL)

    # Fix alias typos by explicit scan
    result = []
    i = 0
    while i < len(fixed):
        if fixed[i:i+4] == "clp.":
            result.append("cp.")
            i += 4
        elif fixed[i:i+4] == "llp.":
            result.append("lp.")
            i += 4
        else:
            result.append(fixed[i])
            i += 1
    fixed = ''.join(result)

    # Alias mismatch: query often selects "p.*" but joins "products lp"
    # Use word boundary to avoid clobbering cp. or lp. into clp. / llp.
    has_p_alias = bool(re.search(r"\b(?:FROM|JOIN)\s+\w+\s+p\b", fixed, flags=re.IGNORECASE))
    m = re.search(r"\bJOIN\s+products\s+(\w+)\b", fixed, flags=re.IGNORECASE)
    if m and not has_p_alias and re.search(r"\bp\.", fixed):
        prod_alias = m.group(1)
        fixed = re.sub(r"\bp\.", f"{prod_alias}.", fixed)

    # Another common mistake: product NAMES are placed into category filters.
    # In our mock data, products.category is "Finance" while names are like "Digital Saving".
    fixed = re.sub(
        r"\b(\w+)\.category\s+IN\s*\(\s*'Digital Saving'\s*,\s*'Digital Lending'\s*,\s*'Investment'\s*,\s*'Insurance'\s*\)",
        r"\1.name IN ('Digital Saving', 'Digital Lending', 'Investment', 'Insurance')",
        fixed,
        flags=re.IGNORECASE,
    )

    # General alias consistency: ensure column prefixes reference a real alias
    alias_map = {}
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+(\w+)\s+(\w+)\b", fixed, re.IGNORECASE):
        alias_map[m.group(2)] = m.group(1)
    prefixes = set(re.findall(r"(?<=\s)(\w+)\.(?=\w)", fixed))
    for prefix in sorted(prefixes, key=len, reverse=True):
        if prefix not in alias_map:
            candidates = [a for a in alias_map if prefix in a]
            if len(candidates) == 1:
                fixed = re.sub(r"\b" + re.escape(prefix) + r"\.", candidates[0] + ".", fixed)

    # In GROUP BY, qualify bare columns that appear qualified in SELECT
    # Use (?<![.\w]) to avoid double-qualifying already-prefixed columns like p.name
    select_m = re.search(r"SELECT\s+(.+?)\s+FROM", fixed, re.IGNORECASE | re.DOTALL)
    group_m = re.search(r"(GROUP\s+BY\s+)(.+?)(?:\s+(?:ORDER|LIMIT|HAVING|;|$))", fixed, re.IGNORECASE | re.DOTALL)
    if select_m and group_m:
        qualified = re.findall(r"(\w+)\.(\w+)", select_m.group(1))
        group_body = group_m.group(2)
        for prefix, col in qualified:
            group_body = re.sub(r"(?<![.\w])" + re.escape(col) + r"(?!\w)", prefix + "." + col, group_body)
        fixed = fixed[:group_m.start(2)] + group_body + fixed[group_m.end(2):]

    return fixed

def _extract_sql_from_llm_output(sql_response: str) -> str:
    """Extract plain SQL from model output, removing markdown wrappers."""
    sql_match = re.search(r"```sql\s*(.+?)\s*```", sql_response, re.DOTALL | re.IGNORECASE)
    if sql_match:
        candidate = sql_match.group(1).strip()
    else:
        candidate = re.sub(r"```.*?\n", "", sql_response)
        candidate = re.sub(r"```", "", candidate).strip()
    return candidate

def _friendly_sql_error(raw: str) -> str:
    """Return clearer message for common SQL generation failures."""
    lower = raw.lower()
    if "syntax error" in lower:
        return "Generated SQL had invalid syntax. Please rephrase your question with simpler wording."
    if "does not exist" in lower or "missing from-clause entry" in lower:
        return "Generated SQL referenced invalid table/column names. Please try your question again."
    return "Failed to run generated SQL safely. Please try a more specific query."

def is_greeting_or_chat(question: str):
    """Simple fallback check if LLM decision fails"""
    q_lower = question.lower().strip()
    
    # greeting 
    simple_checks = ["hi", "hello", "hey", "wow", "cool", "thanks", "thank you", "nice", "great"]
    
    # bot type question
    meta_questions = ["are you a bot", "are you human", "are you real", "are you ai", 
                      "who are you", "what are you"]
    
    return (any(word in q_lower for word in simple_checks) and len(question.split()) < 10) or \
           any(meta in q_lower for meta in meta_questions)

def get_conversational_response(question: str):
    """Generate a helpful conversational response"""
    q_lower = question.lower()
    
    # Greetings
    if any(word in q_lower for word in ["hi", "hello", "hey"]):
        return """👋 Hello! I'm the Deep Insights Copilot for dBank.

I can help you with:
• 📊 Database queries (customer counts, ticket info, product data)
• 🔍 Top root causes and KPI analysis
• 📚 Documentation search

Try asking me:
- "How many customers do we have?"
- "What are the top 5 root causes?"
- "Show me all products"
- "How many open tickets are there?"

What would you like to know?"""
    
    # compliments
    if any(word in q_lower for word in ["useful", "cool", "wow", "amazing", "impressive", "great", "nice"]) and \
       any(word in q_lower for word in ["you", "query", "sql", "can do"]):
        return """😊 Thanks! Yes, I can:

✅ **Generate & execute SQL** from your natural language questions
✅ **Analyze data** and give you natural answers
✅ **Search documentation** semantically
✅ **Answer business questions** about dBank

I'm here to make your work easier! Instead of writing SQL yourself, just ask me questions in plain English and I'll handle the technical details.

What else would you like to know?"""
    
    # bot identity question
    if any(phrase in q_lower for phrase in ["are you a bot", "are you human", "are you real", "are you ai"]):
        return """🤖 I'm an AI assistant (yes, a bot!) built specifically for dBank's operations team.

I'm not a human, but I'm trained to help you with:
✅ Querying customer data and support tickets
✅ Searching dBank documentation and policies
✅ Analyzing KPIs and trends
✅ Generating SQL queries from natural language

Think of me as your AI colleague who has instant access to all dBank data and documentation. I can't make judgment calls like a human, but I can find information and analyze data very quickly!

What can I help you with today?"""
    
    # bot identity question
    if "who are you" in q_lower or "what are you" in q_lower or "introduce" in q_lower:
        return """🤖 I'm the Deep Insights Copilot, an AI assistant built for dBank's operations team.

I have access to:
✅ Customer database (40M customers)
✅ Support tickets (50K/month)
✅ Product information
✅ Knowledge base documentation

I can help you query data, analyze KPIs, and search documentation. What would you like to explore?"""
    
    # what can bot do
    if any(phrase in q_lower for phrase in ["capability", "capabilities", "what can you do", "what do you do", "help", "what can i ask"]):
        return """💡 My Capabilities:

**1. Natural Language to SQL** 🔍
I can understand your questions and generate SQL queries automatically:
- "How many customers do we have?"
- "Show me all products"
- "List open tickets from last month"
- "Write SQL for churned customers in last 30 days"

**2. KPI Analysis** 📊
Get instant insights on support ticket patterns:
- "What are the top 5 root causes?"
- "Show me issue categories with percentages"

**3. Knowledge Base Search** 📚
Search through product documentation:
- "Tell me about Digital Lending"
- "What are known issues?"
- "Explain product policies"

**4. AI Guardrails** 🔒
- ✅ Read-only database access
- ✅ PII masking (emails & names automatically hidden)
- ✅ Parameterized queries (SQL injection protection)
- ✅ All queries logged for audit

**Just ask naturally - I'll handle the rest!** ✨

Example: "How many customers joined last year?" → I'll generate and execute the SQL for you."""
    
    # Default
    return "Hello! I'm here to help with dBank data and insights. What would you like to know?"

def generate_natural_response(question: str, data: any, tool_name: str, client, generated_sql: str = None) -> str:
    """Generate a natural language response from tool results"""
    # Build context for LLM
    context = f"""User asked: "{question}"

Tool used: {tool_name}
"""
    
    if generated_sql:
        context += f"SQL executed: {generated_sql}\n"
    
    context += f"\nData returned:\n{json.dumps(data, indent=2, default=str)[:1000]}"  # avoid token limits
    
    # Generate natural response
    try:
        # Different prompts for KB vs data queries
        if tool_name == "kb.search":
            system_prompt = """You are a dBank support agent. Answer ONLY using the documentation provided.
RULES:
- Use ONLY information from the data provided - never make up details
- If the data doesn't contain the answer, say "I don't have specific information about that in our knowledge base"
- Quote specific details from the docs (file sizes, formats, procedures)
- Be helpful but stay grounded in dBank documentation
- Sound professional but friendly"""
        else:
            system_prompt = """You are a dBank business analyst. Answer naturally based on the data provided.
- Be friendly and concise
- For lists, summarize key points
- Use natural language, not JSON
- Sound like a helpful colleague"""
        
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{context}\n\nProvide a natural, helpful answer (2-3 sentences):"}
            ],
            temperature=0.3,  # low tem for reduceing hallu 
            max_tokens=min(settings.GROQ_MAX_TOKENS, 256)
        ).choices[0].message.content
        
        return response
    except Exception as e:
        #  fallback responses
        logger.warning(f"Natural response generation failed: {e}")
        
        if not data or (isinstance(data, list) and len(data) == 0):
            return "I couldn't find any matching data for that question. Try asking about our customers, tickets, or products!"
        
        # simple  fallback
        if isinstance(data, list):
            count = len(data)
            if count == 1:
                return f"I found 1 record. Check the data below for details."
            else:
                return f"I found {count} records matching your question. See the data section below for details."
        
        return "I found some data for your question. Check the results below!"

def select_tool_by_keywords(question: str):
    """Simple keyword-based tool selection as fallback"""
    q_lower = question.lower()
    
    kpi_words = ["top", "root cause", "category", "categories", "issue", "kpi", "percentage", "distribution"]
    if any(word in q_lower for word in kpi_words):
        return "kpi.top_root_causes", "Question asks about top root causes or categories"
    
    kb_words = [
        "what is", "what are", "tell me about", "explain", "policy", "policies",
        "documentation", "known issue", "known issues", "how to", "how do i",
        "troubleshoot", "guide", "manual", "feature", "product",
    ]
    if any(word in q_lower for word in kb_words):
        return "kb.search", "Question asks about documentation or policies"
    
    sql_words = ["list", "show", "count", "how many", "how much", "total", "average",
                 "find", "get", "give me", "what", "which", "when", "all"]
    if any(word in q_lower for word in sql_words):
        return "sql.query", "Question asks to query database"
    
    return "sql.query", "Question asks about data (count, list, show, etc.)"

async def _log_request(question: str, tool: str, latency_ms: int, success: bool, error_text: str | None = None):
    def _insert():
        with sync_engine.connect() as conn:
            conn.execute(
                text("INSERT INTO request_logs (question, tool_used, latency_ms, success, error) VALUES (:q, :t, :l, :s, :e)"),
                {"q": question, "t": tool, "l": latency_ms, "s": success, "e": error_text},
            )
            conn.commit()
    try:
        await asyncio.to_thread(_insert)
    except Exception as e:
        logger.warning(f"Failed to log request: {e}")


@router.post("/ask")
async def ask_question(payload: AskPayload, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _request_log[client_ip]
    while window and now - window[0] > _RATE_LIMIT_WINDOW_SECONDS:
        window.popleft()
    if len(window) >= _RATE_LIMIT_MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "tool_used": "rate_limiter",
                "data": [],
                "answer": "Too many requests. Please wait a minute before trying again.",
                "message": "Rate limit exceeded (10 requests per minute).",
            },
        )
    window.append(now)

    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    question = payload.question
    history = payload.history

    # Format conversation history for context
    history_lines = []
    if history:
        for msg in history[-6:]:  # last 6 turns to avoid token overflow
            role = msg.get("role", "")
            content = (msg.get("content") or msg.get("answer") or "").strip()
            if content:
                history_lines.append(f"{role.capitalize()}: \"{content[:200]}\"")
    if history_lines:
        history_context = "\n".join(history_lines) + "\n"
    else:
        history_context = ""

    tool_list = ", ".join(TOOLS.keys())

    # llm will choose the tool
    try:
        decision_prompt = f"""You are a dBank support agent AI. Decide how to handle this question intelligently.

Previous conversation:
{history_context}User asked: "{question}"

Available tools:
- sql.query: Query customer/ticket/product/login data from database
- kb.search: Search documentation about products/policies/troubleshooting
- kpi.top_root_causes: Get top 5 issue categories with percentages

DECISION RULES (use contextual intelligence):

1. Use "chat" for META-QUESTIONS about the bot/AI itself:
   - "Are you a bot?" "Who are you?" "How do you work?" "Are you human?"
   - Greetings: "Hi" "Hello" "Good morning"
   - Compliments: "You're helpful" "Thanks" "Good job"
   - Capability questions: "What can you do?" "How can you help?"
   Example: {{"action": "chat", "response": "I'm an AI assistant for dBank..."}}

2. Use "kb.search" for dBank-SPECIFIC questions:
   - Product features: "What is Digital Lending?" "Tell me about Digital Saving"
   - Policies: "What are the fees?" "What's the loan limit?" "Interest rates?"
   - Troubleshooting: "I can't upload" "App is slow" "Notifications not working"
   - Known issues: "What's wrong with v1.2?" "Why is interest delayed?"
   Example: {{"action": "tool", "tool_name": "kb.search", "reason": "needs product/policy info"}}

3. Use "sql.query" for DATA questions:
   - Counts: "How many customers?" "How many tickets?"
   - Lists: "Show me products" "List open tickets"
   - Stats: "Average loan amount" "Ticket volume"
   Example: {{"action": "tool", "tool_name": "sql.query", "reason": "needs database query"}}

4. Use "kpi.top_root_causes" for:
   - "Top root causes" "Main issues" "Top 5 problems"
   Example: {{"action": "tool", "tool_name": "kpi.top_root_causes", "reason": "needs KPI analysis"}}

CRITICAL RULES:
- If question is about YOU (the AI), use "chat" - don't search KB!
- If question is about dBank products/policies, ALWAYS use "kb.search" - never make up info!
- If question needs data/numbers, use "sql.query" or "kpi.top_root_causes"
- Be intelligent - understand the INTENT, not just keywords!"""

        llm_decision = (await _groq_chat_create_with_backoff(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a decision-making assistant. Always respond with valid JSON."},
                {"role": "user", "content": decision_prompt}
            ],
            temperature=0.3
        )).choices[0].message.content

        # return json from response
        if "{" in llm_decision:
            json_start = llm_decision.index("{")
            json_end = llm_decision.rindex("}") + 1
            llm_decision = llm_decision[json_start:json_end]
        
        decision = json.loads(llm_decision)
        
        # LLm return normal chat reponse if it says just chat
        if decision.get("action") == "chat":
            latency_ms = int((time.time() - start_time) * 1000)
            ACTIVE_REQUESTS.dec()
            REQUEST_COUNT.labels(tool="conversational").inc()
            REQUEST_LATENCY.labels(tool="conversational").observe(latency_ms / 1000.0)
            asyncio.create_task(_log_request(question, "conversational", latency_ms, True, None))
            return {
                "tool_used": "conversational",
                "answer": decision.get("response", "I'm here to help! What would you like to know?"),
                "reason": "Direct conversational response"
            }
        
        # else use tol
        tool_name = decision.get("tool_name", "sql.query")
        reason = decision.get("reason", "LLM selected this tool")
        
    except Exception as e:
        logger.warning(f"LLM decision failed, using fallback: {str(e)}")
        
        # for greetings
        if is_greeting_or_chat(question):
            response_text = get_conversational_response(question)
            latency_ms = int((time.time() - start_time) * 1000)
            ACTIVE_REQUESTS.dec()
            REQUEST_COUNT.labels(tool="conversational").inc()
            REQUEST_LATENCY.labels(tool="conversational").observe(latency_ms / 1000.0)
            asyncio.create_task(_log_request(question, "conversational", latency_ms, True, None))
            return {
                "tool_used": "conversational",
                "answer": response_text,
                "reason": "Greeting or chat detected"
            }
        
        # else use tool
        tool_name, reason = select_tool_by_keywords(question)
        decision = {"chosen_tool": tool_name, "reason": reason}
    
    # execute the selected tool with llm assistance
    generated_sql = None  # tracking the sql command
    try:
        if tool_name == "sql.query":
            # Use LLM to generate SQL from natural language
            sql_prompt = f"""Generate a PostgreSQL SELECT query for this question: "{question}"

Previous conversation:
{history_context}Available tables and schema:

1. customers (id, name, email, region, joined_date, age, income, occupation, phone)
   - age: customer age in years (integer)
   - income: monthly income in THB
   - occupation: job title

2. tickets (id, customer_id, product_id, category, issue, status, priority, 
            created_at, resolved_at, assigned_to, app_version)
   - app_version: 'v1.1' or 'v1.2' (v1.2 released on Jan 15, 2025)
   - priority: 'low', 'medium', 'high', 'critical'
   - created_at: timestamp when ticket was created
   - resolved_at: timestamp when ticket was resolved (NULL if still open)

3. logins (id, customer_id, last_login, login_count)

4. products (id, name, category)
   - Products: Digital Saving, Digital Lending, Investment, Insurance

5. customer_products (id, customer_id, product_id, enrolled_date, status)
   - IMPORTANT: customer_products does NOT have product_name/category; join products via customer_products.product_id = products.id

6. transactions (id, customer_id, product_id, amount, type, method, description, created_at, status)
   - amount: transaction value in THB (DECIMAL) -- use t.amount, NOT t.transaction_value
   - type: 'deposit', 'withdrawal', 'transfer', 'payment'
   - method: 'PromptPay', 'app_transfer', 'ATM', 'counter', 'auto_debit'
   - created_at: timestamp when transaction occurred -- use t.created_at, NOT t.transaction_date
   - status: 'completed', 'pending', 'failed'

7. escalations (id, ticket_id, escalated_to, reason, escalated_at, resolved_at)
   - escalated_to: 'L2_Support', 'Engineering', 'Compliance', 'Security'
   - reason: escalation reason text

Important context:
- Virtual Bank App v1.2 was released on January 15, 2025
- To analyze spike, compare ticket volumes before/after Jan 15
- Use DATE() to group by day, app_version to filter by version
- Join with products table to show product names
- IMPORTANT joins:
  - customers.id joins to tickets.customer_id (NOT tickets.customer)
  - customers.id joins to logins.customer_id
  - customers.id joins to transactions.customer_id
  - tickets.id joins to escalations.ticket_id

SQL OUTPUT RULES:
- Return ONLY one PostgreSQL query, no markdown, no explanation
- Query MUST start with SELECT or WITH
- Use ONLY columns listed above
- Never use "AS alias" inside GROUP BY
- Use tickets.customer_id and logins.customer_id for customer joins
- KEEP IT SIMPLE: For basic counts/lists, write a single-table query.
  Only add JOINs when the question explicitly mentions multiple entities.
- NEVER use EXTRACT(), DATE(), or any function in GROUP BY -- causes syntax errors.
  Always GROUP BY plain column names only (e.g. GROUP BY t.status, p.name).
- Prefix all column references with their table alias (e.g. t.status, cp.status).
- Use t.amount NOT t.transaction_value
- Use t.created_at NOT t.transaction_date

Always write the SIMPLEST query that answers the question. Examples:
  "how many customers" → SELECT COUNT(*) AS total FROM customers
  "show me products"  → SELECT * FROM products
  "list open tickets" → SELECT * FROM tickets WHERE status = 'open'
  "total transaction value" → SELECT SUM(amount) FROM transactions

Return ONLY the SQL query."""

            sql_response = (await _groq_chat_create_with_backoff(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate clean PostgreSQL queries."},
                    {"role": "user", "content": sql_prompt}
                ],
                temperature=0,
                max_tokens=min(settings.GROQ_MAX_TOKENS, 256),
            )).choices[0].message.content.strip()
            
            generated_sql = _extract_sql_from_llm_output(sql_response)

            # Quick guardrail: common hallucinated columns for this schema
            # If the LLM tries to select customer_products.product_name/category, rewrite to products.name/category
            # and ensure products is joined.
            if "customer_products" in generated_sql and ("product_name" in generated_sql or "lp.product_name" in generated_sql):
                generated_sql = generated_sql.replace("lp.product_name", "p.name AS product_name")
                generated_sql = generated_sql.replace("lp.category", "p.category")
                if " join products " not in generated_sql.lower() and " join products\n" not in generated_sql.lower():
                    generated_sql = generated_sql.replace(
                        "LEFT JOIN customer_products lp ON c.id = lp.customer_id",
                        "LEFT JOIN customer_products lp ON c.id = lp.customer_id\n  LEFT JOIN products p ON lp.product_id = p.id",
                    )

            # Another common hallucination: tickets.customer instead of tickets.customer_id
            # Fix only the alias form to avoid unintended replacements.
            generated_sql = generated_sql.replace("t.customer ", "t.customer_id ")
            generated_sql = generated_sql.replace("t.customer\n", "t.customer_id\n")
            generated_sql = generated_sql.replace("t.customer)", "t.customer_id)")
            generated_sql = generated_sql.replace("t.customer,", "t.customer_id,")

            generated_sql = _sanitize_generated_sql(generated_sql)
            if not _is_read_query(generated_sql):
                raise ValueError("Generated query is not read-only (SELECT/WITH only).")
            
            result = await sql_query(generated_sql)
            
            # gen the natural response
            answer = generate_natural_response(question, result, tool_name, client, generated_sql)

            latency_ms = int((time.time() - start_time) * 1000)
            ACTIVE_REQUESTS.dec()
            REQUEST_COUNT.labels(tool=tool_name).inc()
            REQUEST_LATENCY.labels(tool=tool_name).observe(latency_ms / 1000.0)
            asyncio.create_task(_log_request(question, tool_name, latency_ms, True, None))
            return {
                "tool_used": tool_name,
                "answer": answer,
                "data": result,
                "generated_sql": generated_sql,
                "reason": reason
            }
            
        elif tool_name == "kpi.top_root_causes":
            result = await kpi_top_root_causes()
            
            # gen the natural response
            answer = generate_natural_response(question, result, tool_name, client)

            latency_ms = int((time.time() - start_time) * 1000)
            ACTIVE_REQUESTS.dec()
            REQUEST_COUNT.labels(tool=tool_name).inc()
            REQUEST_LATENCY.labels(tool=tool_name).observe(latency_ms / 1000.0)
            asyncio.create_task(_log_request(question, tool_name, latency_ms, True, None))
            return {
                "tool_used": tool_name,
                "answer": answer,
                "data": result,
                "reason": reason
            }
            
        elif tool_name == "kb.search":
            result = await kb_search(question)
            
            # gen the response from kb result
            if not result:
                answer = "I don't have information about that in my knowledge base. I can help you with questions about our customer data, tickets, or products instead."
            else:
                answer = generate_natural_response(question, result, tool_name, client)
            
            latency_ms = int((time.time() - start_time) * 1000)
            ACTIVE_REQUESTS.dec()
            REQUEST_COUNT.labels(tool=tool_name).inc()
            REQUEST_LATENCY.labels(tool=tool_name).observe(latency_ms / 1000.0)
            asyncio.create_task(_log_request(question, tool_name, latency_ms, True, None))
            return {
                "tool_used": tool_name,
                "answer": answer,
                "data": result if result else [],
                "reason": reason
            }
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        
        answer_msg = f"Error: {str(e)}"
        if tool_name == "sql.query":
            answer_msg = _friendly_sql_error(str(e))

        latency_ms = int((time.time() - start_time) * 1000)
        ACTIVE_REQUESTS.dec()
        REQUEST_COUNT.labels(tool=tool_name if tool_name else "unknown").inc()
        REQUEST_LATENCY.labels(tool=tool_name if tool_name else "unknown").observe(latency_ms / 1000.0)
        ERROR_COUNT.labels(type=type(e).__name__).inc()
        asyncio.create_task(_log_request(question, tool_name if tool_name else "unknown", latency_ms, False, str(e)))

        error_response = {
            "error": str(e),
            "error_type": type(e).__name__,
            "tool_used": tool_name if tool_name else "unknown",
            "data": [],
            "answer": answer_msg,
            "message": "An error occurred while processing your question."
        }
        
        # return the sql command if available
        if generated_sql:
            error_response["generated_sql"] = generated_sql
        
        return error_response
