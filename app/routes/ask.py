from fastapi import APIRouter
from groq import Groq
from app.mcp_tools import sql_query, kb_search, kpi_top_root_causes
from app.config import settings
from pydantic import BaseModel

router = APIRouter()
client = Groq(api_key=settings.GROQ_API_KEY)
# define tools
TOOLS = {
    "sql.query": sql_query,
    "kb.search": kb_search,
    "kpi.top_root_causes": kpi_top_root_causes
}

class AskPayload(BaseModel):
    question: str

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
    import json
    
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
            model="groq/compound",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{context}\n\nProvide a natural, helpful answer (2-3 sentences):"}
            ],
            temperature=0.3,  # low tem for reduceing hallu 
            max_tokens=200
        ).choices[0].message.content
        
        return response
    except Exception as e:
        #  fallback responses
        import logging
        logging.getLogger(__name__).warning(f"Natural response generation failed: {e}")
        
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
    
    # Check for KPI/root cause keywords
    if any(word in q_lower for word in ["top", "root cause", "category", "categories", "issue"]):
        return "kpi.top_root_causes", "Question asks about top root causes or categories"
    
    # Check for KB/documentation keywords
    if any(word in q_lower for word in ["what is", "tell me about", "explain", "policy", "documentation", "known issue"]):
        return "kb.search", "Question asks about documentation or policies"
    
    # Default to SQL for data queries
    return "sql.query", "Question asks about data (count, list, show, etc.)"

@router.post("/ask")
async def ask_question(payload: AskPayload):
    question = payload.question
    tool_list = ", ".join(TOOLS.keys())

    # llm will choose the tool
    try:
        decision_prompt = f"""You are a dBank support agent AI. Decide how to handle this question intelligently.

User asked: "{question}"

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

        llm_decision = client.chat.completions.create(
            model="groq/compound",
            messages=[
                {"role": "system", "content": "You are a decision-making assistant. Always respond with valid JSON."},
                {"role": "user", "content": decision_prompt}
            ],
            temperature=0.3
        ).choices[0].message.content

        import json
        import re
        
        # return json from response
        if "{" in llm_decision:
            json_start = llm_decision.index("{")
            json_end = llm_decision.rindex("}") + 1
            llm_decision = llm_decision[json_start:json_end]
        
        decision = json.loads(llm_decision)
        
        # LLm return normal chat reponse if it says just chat
        if decision.get("action") == "chat":
            return {
                "tool_used": "conversational",
                "answer": decision.get("response", "I'm here to help! What would you like to know?"),
                "reason": "Direct conversational response"
            }
        
        # else use tol
        tool_name = decision.get("tool_name", "sql.query")
        reason = decision.get("reason", "LLM selected this tool")
        
    except Exception as e:
        # check if obviously conversational
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"LLM decision failed, using fallback: {str(e)}")
        
        # for greetings
        if is_greeting_or_chat(question):
            response_text = get_conversational_response(question)
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

Available tables and schema:

1. customers (id, name, email, region, joined_date)

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

Important context:
- Virtual Bank App v1.2 was released on January 15, 2025
- To analyze spike, compare ticket volumes before/after Jan 15
- Use DATE() to group by day, app_version to filter by version
- Join with products table to show product names

Return ONLY the SQL SELECT query, nothing else. Use proper JOINs when needed."""

            sql_response = client.chat.completions.create(
                model="groq/compound",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate clean PostgreSQL queries."},
                    {"role": "user", "content": sql_prompt}
                ],
                temperature=0
            ).choices[0].message.content.strip()
            
            # sql remove markdown if present
            import re
            sql_match = re.search(r'```sql\n(.+?)\n```', sql_response, re.DOTALL)
            if sql_match:
                generated_sql = sql_match.group(1).strip()
            else:
                # remove any md code blocks
                generated_sql = re.sub(r'```.*?\n', '', sql_response)
                generated_sql = re.sub(r'```', '', generated_sql).strip()
            
            result = await sql_query(generated_sql)
            
            # gen the natural response
            answer = generate_natural_response(question, result, tool_name, client, generated_sql)
            
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
            
            return {
                "tool_used": tool_name,
                "answer": answer,
                "data": result if result else [],
                "reason": reason
            }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        
        error_response = {
            "error": str(e),
            "error_type": type(e).__name__,
            "tool_used": tool_name,
            "data": [],
            "answer": f"Error: {str(e)}",
            "message": "An error occurred while processing your question."
        }
        
        # return the sql command if available
        if generated_sql:
            error_response["generated_sql"] = generated_sql
        
        return error_response
