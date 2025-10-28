"""
Basic tests for Hisaab application
"""
import pytest
from app.agent.graph import agent
from app.database.setup import create_database


def test_agent_creation():
    """Test that agent is created successfully"""
    assert agent is not None


def test_database_creation():
    """Test database creation"""
    try:
        create_database("test_local_database/test_hisaab.db")
        assert True
    except Exception as e:
        pytest.fail(f"Database creation failed: {e}")


def test_agent_invoke():
    """Test basic agent invocation"""
    try:
        config = {"configurable": {"thread_id": "test123"}}
        response = agent.invoke(
            {
                "messages": [{"role": "user", "content": "سلام"}], 
                "phone_number": "923008224731"
            }, 
            config
        )
        assert response is not None
        assert "messages" in response
    except Exception as e:
        pytest.fail(f"Agent invocation failed: {e}")
