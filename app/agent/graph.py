"""
LangGraph agent construction and compilation
"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from .state import State
from .tools import get_sql_tools, get_memory_checkpointer
from .prompt import SYSTEM_PROMPT

load_dotenv()

# Constants
SHOPKEEPER_PHONE = "92300822473" # Fallback phone-number in case of error
MODEL_NAME = "gpt-4o"


def create_hisaab_agent():
    """Create and compile the Hisaab LangGraph agent"""
    
    # Get tools and memory
    tools = get_sql_tools()
    memory = get_memory_checkpointer()
    
    # Initialize LLM with tools
    llm = ChatOpenAI(model=MODEL_NAME)
    llm_with_tools = llm.bind_tools(tools)
    
    # Create graph builder
    graph_builder = StateGraph(State)
    
    def hisaab_agent_node(state: State):
        """Agent node with comprehensive message history handling"""
        phone = state.get('phone_number')
        system_prompt = SYSTEM_PROMPT.format(shopkeeper_phone=phone)
        
        messages = state['messages']
        
        # Trim messages to stay within token limits
        trimmed_messages = trim_messages(
            messages,
            max_tokens=500,
            strategy="last",
            token_counter=count_tokens_approximately,
            start_on="human",
            include_system=True,
            allow_partial=False,
        )

        response = llm_with_tools.invoke([SystemMessage(content=system_prompt)] + trimmed_messages)
        
        return {"messages": [response]}

    def should_continue(state: State) -> str:
        """
        Conditional edge function that determines:
        - If the agent wants to use tools -> route to 'tools'
        - If the agent is done -> route to END
        """
        last_message = state["messages"][-1]
        
        if not last_message.tool_calls:
            return END
        else:
            return "tools"

    # Add nodes
    graph_builder.add_node("agent", hisaab_agent_node)
    
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    # Add edges
    graph_builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph_builder.add_edge("tools", "agent")
    graph_builder.set_entry_point("agent")

    # Compile with persistent memory
    return graph_builder.compile(checkpointer=memory)


# Create the agent instance
agent = create_hisaab_agent()
