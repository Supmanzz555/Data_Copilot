from fastapi import APIRouter
from app.mcp_tools import sql_query, kb_search, kpi_top_root_causes

router = APIRouter()

TOOLS = {
    "sql.query": {"description": "Execute read-only SQL with parameters"},
    "kb.search": {"description": "Search knowledge base documents"},
    "kpi.top_root_causes": {"description": "Top root causes of issues"}
}

@router.get("/tools/list")
async def list_tools():
    return {"tools": TOOLS}

@router.post("/tools/call")
async def call_tool(payload: dict):
    name = payload.get("name")
    param = payload.get("params", {})
    if name == "sql.query":
        return await sql_query(param.get("query", "SELECT 1"))
    elif name == "kb.search":
        return await kb_search(param.get("query", ""))
    elif name == "kpi.top_root_causes":
        return await kpi_top_root_causes()
    return {"error": "Invalid tool name"}
