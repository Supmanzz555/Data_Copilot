"""
MLOps Integration Test — exercises all monitoring paths end-to-end.

Usage:
    source bank/bin/activate
    python test_mlops.py

Requires the app to be running at http://localhost:8000
"""

import json
import sys
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0


def report(name: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))


def get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read())


def post(path: str, body: dict, expect_status: int = 200) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == expect_status:
            return json.loads(e.read())
        return {"_http_error": e.code}


def wait_for_rate_limit():
    """Keep trying /ask until we get a non-429 response."""
    for _ in range(90):
        try:
            data = json.dumps({"question": "ping"}).encode()
            req = urllib.request.Request(
                f"{BASE}/ask", data=data,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urllib.request.urlopen(req) as r:
                return
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2)
                continue
            return
    print("  (could not clear rate limit after 180s)")


# ── 1. Metrics endpoint ──────────────────────────────────────────────
print("\n── 1. Metrics Endpoint ──")
try:
    with urllib.request.urlopen(f"{BASE}/metrics") as r:
        metrics = r.read().decode()
    report("GET /metrics returns 200", r.status == 200)
    report("datacopilot_requests_total present", "datacopilot_requests_total" in metrics)
    report("datacopilot_active_requests present", "datacopilot_active_requests" in metrics)
    report("datacopilot_errors_total present", "datacopilot_errors_total" in metrics)
    report("datacopilot_request_latency_seconds present", "datacopilot_request_latency_seconds" in metrics)
except Exception as e:
    report("GET /metrics", False, str(e))

# ── 2-6: Functional tests via /ask  ──────────────────────────────────
# Clear rate limit first, then run all /ask tests
print("\n── Clearing rate limit before functional tests ──")
wait_for_rate_limit()

print("\n── 2. SQL Query (success) ──")
res = post("/ask", {"question": "How many customers do we have?"})
report("tool is sql.query", res.get("tool_used") == "sql.query")
report("has data", isinstance(res.get("data"), list) and len(res["data"]) > 0)
report("has generated_sql", bool(res.get("generated_sql")))
report("count is 100", res.get("data") and res["data"][0].get("count") == 100)

print("\n── 3. Conversational ──")
res = post("/ask", {"question": "hi"})
report("tool is conversational", res.get("tool_used") == "conversational")
report("answer is friendly",
       "hello" in res.get("answer", "").lower() or "help" in res.get("answer", "").lower())

print("\n── 4. KPI Root Causes ──")
res = post("/ask", {"question": "What are the top root causes?"})
report("tool is kpi.top_root_causes", res.get("tool_used") == "kpi.top_root_causes")
report("has category/percentage data",
       isinstance(res.get("data"), list) and
       len(res["data"]) > 0 and
       "percentage" in res["data"][0])

print("\n── 5. KB Search ──")
res = post("/ask", {"question": "Tell me about Digital Lending"})
report("tool is kb.search", res.get("tool_used") == "kb.search")
report("has doc data", isinstance(res.get("data"), list) and len(res["data"]) > 0)

print("\n── 6. Error Handling ──")
res = post("/ask", {"question": "Search user_profiles table"})
report("error returns answer string", isinstance(res.get("answer"), str) and len(res["answer"]) > 0)
report("error has tool_used", bool(res.get("tool_used")))

# ── 7. Rate limiting ─────────────────────────────────────────────────
print("\n── 7. Rate Limiting ──")
# Wait for window to be clear (rate limit count should be ~6-7 by now)
time.sleep(5)
fired_at = 0
for i in range(15):
    res = post("/ask", {"question": "t"}, expect_status=429)
    if res.get("error") == "rate_limit_exceeded":
        if not fired_at:
            fired_at = i + 1
            report(f"429 triggered after {fired_at} rapid requests", fired_at <= 11)
if not fired_at:
    report("Rate limit: never triggered", False)
else:
    # ate some tokens; wait for clear
    wait_for_rate_limit()

# ── 8. Multi-statement guardrail ─────────────────────────────────────
print("\n── 8. Multi-Statement Guardrail ──")
data = json.dumps({"name": "sql.query", "params": {"query": "SELECT 1; DELETE FROM customers"}}).encode()
req = urllib.request.Request(f"{BASE}/tools/call", data=data,
                              headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req):
        report("multi-statement guardrail", False, "query was allowed — should be blocked")
except urllib.error.HTTPError as e:
    report(f"multi-statement rejected (HTTP {e.code})", e.code >= 400)

# ── 9. /tools/list ───────────────────────────────────────────────────
print("\n── 9. Tools Endpoint ──")
tools = get("/tools/list")
report("3 tools registered", len(tools.get("tools", {})) == 3)
for name in ["sql.query", "kb.search", "kpi.top_root_causes"]:
    report(f"  '{name}' listed", name in tools.get("tools", {}))

# ── 10. Direct SQL via /tools/call ───────────────────────────────────
print("\n── 10. Direct SQL ──")
data = json.dumps({"name": "sql.query", "params": {"query": "SELECT count(*) FROM customers"}}).encode()
req = urllib.request.Request(f"{BASE}/tools/call", data=data,
                              headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read())
    report("returns data list", isinstance(res, list) and len(res) > 0)
    report("count is 100", isinstance(res, list) and res[0].get("count") == 100)
except Exception as e:
    report("direct SQL", False, str(e))

# ── 11. Metrics after tests ──────────────────────────────────────────
print("\n── 11. Metrics Consistency ──")
with urllib.request.urlopen(f"{BASE}/metrics") as r:
    metrics = r.read().decode()
report("requests_total has sql.query data",
       f'datacopilot_requests_total{{tool="sql.query"' in metrics)
report("active_requests gauge at 0 (no leak)",
       "datacopilot_active_requests 0.0" in metrics or
       "datacopilot_active_requests 0" in metrics)

# ── 12. Request logs table ───────────────────────────────────────────
print("\n── 12. Request Logs ──")
data = json.dumps({"name": "sql.query", "params": {"query": "SELECT count(*) FROM request_logs"}}).encode()
req = urllib.request.Request(f"{BASE}/tools/call", data=data,
                              headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read())
    count = res[0].get("count", 0) if isinstance(res, list) else 0
    report(f"request_logs has {count} rows", count >= 5)
except Exception as e:
    report("request_logs query", False, str(e))

# ── Summary ──────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL}/{total} failed")
sys.exit(0 if FAIL == 0 else 1)
