"""
SQL tools and utilities for the Hisaab agent
"""
import os
import sqlite3
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.sqlite import SqliteSaver


# Constants
DB_PATH = "app/local_database/agent_memory.db"
DB_URI = "sqlite:///app/local_database/hisaab.db"
MODEL_NAME = "gpt-4o"



def get_memory_checkpointer():
    """Get SqliteSaver for persistent memory"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return SqliteSaver(conn)


def get_sql_tools():
    """Get SQL tools for the agent"""
    db = SQLDatabase.from_uri(DB_URI)
    llm = ChatOpenAI(model=MODEL_NAME)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    return [tool for tool in tools if tool.__class__.__name__ != "QuerySQLCheckerTool"]
