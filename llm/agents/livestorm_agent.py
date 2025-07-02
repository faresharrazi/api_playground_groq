"""
Livestorm Agent for LangChain integration
"""

import os
from typing import List, Dict, Any, Optional
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from ..tools.tools_factory import create_livestorm_tools


class LivestormAgent:
    """Agent for interacting with Livestorm API through natural language"""
    
    def __init__(self, groq_api_key: str, livestorm_api_key: str):
        """
        Initialize the Livestorm agent
        
        Args:
            groq_api_key: Groq API key for LLM
            livestorm_api_key: Livestorm API key for tools
        """
        self.groq_api_key = groq_api_key
        self.livestorm_api_key = livestorm_api_key
        
        # Initialize the LLM
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.1
        )
        
        # Create tools
        self.tools = create_livestorm_tools(livestorm_api_key)
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Custom system prompt
        system_message = (
            "You are a helpful assistant that can interact with the Livestorm API. "
            "You have access to tools that can list events, sessions, and people. "
            "IMPORTANT: The list_events tool ALWAYS fetches ALL events across ALL pages, regardless of any page_number input. "
            "NEVER try to paginate or call this tool in a loop. Call it ONCE and it will return a summary of all events. "
            "If you want to filter, use the filter parameters. If you want all events, just call it with no filters. "
            "Never try to increment page numbers yourself!"
        )
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=1,
            system_message=system_message
        )
        
        # Note: System prompt is handled automatically by LangChain
    
    def ask(self, question: str) -> str:
        """
        Ask a question to the agent
        
        Args:
            question: The user's question
            
        Returns:
            The agent's response
        """
        try:
            response = self.agent.run(question)
            return response
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question."
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history
        
        Returns:
            List of conversation messages
        """
        return self.memory.chat_memory.messages


def create_livestorm_agent(groq_api_key: Optional[str] = None, livestorm_api_key: Optional[str] = None) -> LivestormAgent:
    """
    Create a Livestorm agent with API keys
    
    Args:
        groq_api_key: Groq API key (will use environment variable if not provided)
        livestorm_api_key: Livestorm API key (will use environment variable if not provided)
        
    Returns:
        Configured LivestormAgent instance
    """
    # Get API keys from environment if not provided
    groq_key = groq_api_key or os.getenv("GROQ_API_KEY")
    livestorm_key = livestorm_api_key or os.getenv("LS_API_KEY")
    
    if not groq_key:
        raise ValueError("GROQ_API_KEY is required")
    if not livestorm_key:
        raise ValueError("LS_API_KEY is required")
    
    return LivestormAgent(groq_key, livestorm_key) 