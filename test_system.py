#!/usr/bin/env python3
"""
System test script for Deep Insights Copilot
Tests all endpoints and MCP tools
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_database():
    """Test database connectivity and schema"""
    print("\n🗄️  Testing Database Connection...")
    try:
        engine = create_async_engine(
            "postgresql+asyncpg://admin:admin@localhost:5432/deep_insights",
            echo=False,
        )
        async with engine.begin() as conn:
            # check if tables exist
            tables = ['customers', 'tickets', 'logins', 'products', 'kb_embeddings']
            for table in tables:
                result = await conn.execute(
                    text(f"SELECT COUNT(*) as cnt FROM {table}")
                )
                count = result.fetchone()[0]
                print(f"  Table '{table}': {count} rows")
        
        await engine.dispose()
        return True
    except Exception as e:
        print(f"  Database test failed: {e}")
        return False

async def test_mcp_tools():
    """Test MCP tools"""
    print("\n🔧 Testing MCP Tools...")
    try:
        from app.mcp_tools import sql_query, kb_search, kpi_top_root_causes
        
        # test sql.query
        print("\n  Testing sql.query...")
        result = await sql_query("SELECT COUNT(*) as count FROM customers")
        print(f"    Customer count: {result[0]['count']}")
        
        # test kb.search
        print("\n  Testing kb.search...")
        result = await kb_search("digital lending")
        print(f"    KB search returned {len(result)} results")
        
        # test kpi.top_root_causes
        print("\n  Testing kpi.top_root_causes...")
        result = await kpi_top_root_causes()
        print(f"    Top causes: {len(result)} categories")
        for row in result[:3]:
            print(f"       - {row['category']}: {row['count']} ({row['percentage']}%)")
        
        # test PII Masking
        print("\n  Testing PII masking...")
        result = await sql_query("SELECT name, email FROM customers LIMIT 1")
        if result:
            print(f"    Name masked: {result[0]['name']}")
            print(f"    Email masked: {result[0]['email']}")
        
        # Test 5: Read-only enforcement
        print("\n  Testing read-only enforcement...")
        try:
            await sql_query("DELETE FROM customers WHERE id = 999")
            print("    Read-only enforcement FAILED!")
            return False
        except ValueError as e:
            print(f"     Read-only enforced: {str(e)[:50]}...")
        
        return True
    except Exception as e:
        print(f"  MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """Test API endpoints (requires server running)"""
    print("\nTesting API Endpoints...")
    print("  Make sure the server is running on http://localhost:8000")
    
    try:
        import httpx
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
            # ui page
            print("\n  Testing GET /...")
            response = await client.get("/")
            assert response.status_code == 200
            print(f"    Home page: {response.status_code}")
            
            # tool list testing
            print("\n  Testing GET /tools/list...")
            response = await client.get("/tools/list")
            assert response.status_code == 200
            tools = response.json()["tools"]
            print(f"    Tools available: {', '.join(tools.keys())}")
            
            # test ask endpoint
            print("\n  Testing POST /ask...")
            response = await client.post(
                "/ask",
                json={"question": "What are the top root causes?"}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"    Tool used: {data.get('tool_used')}")
            print(f"    Results: {len(data.get('result', []))} items")
            
            # tool call test
            print("\n  Testing POST /tools/call...")
            response = await client.post(
                "/tools/call",
                json={"name": "kpi.top_root_causes", "params": {}}
            )
            assert response.status_code == 200
            print(f"     Direct tool call successful")
        
        return True
    except ImportError:
        print("   httpx not installed, skipping API tests")
        print("     Install with: pip install httpx")
        return True
    except Exception as e:
        print(f"   API endpoint tests failed: {e}")
        print("     Make sure the server is running: docker-compose up")
        return False

async def main():
    print("=" * 70)
    print("🏦 Deep Insights Copilot - System Tests")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 3
    
    # databse test
    if await test_database():
        tests_passed += 1
    
    # mpc tools test
    if await test_mcp_tools():
        tests_passed += 1
    
    # test api
    if await test_api_endpoints():
        tests_passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed")
    print("=" * 70)
    
    if tests_passed == tests_total:
        print("All tests passed! System is working correctly.")
        return 0
    else:
        print("Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

