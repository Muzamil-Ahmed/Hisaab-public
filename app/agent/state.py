"""
LangGraph State definitions for the Hisaab agent
"""
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class State(TypedDict):
    """State schema for the Hisaab LangGraph agent"""
    messages: Annotated[list[AnyMessage], add_messages]
    phone_number: str
