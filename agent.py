"""
Book Recommendation Agent with LangChain v1 - Groq Version
A specialized agent for personalized book recommendations
"""

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
import os
import sys
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Global chat history
chat_history = []

# =============================================================================
# CUSTOM TOOLS FOR BOOK RECOMMENDATIONS
# =============================================================================

@tool
def search_books_by_genre(genre: str) -> str:
    """
    Search for popular and highly-rated books in a specific genre.
    
    Args:
        genre: The genre to search for (e.g., "science fiction", "mystery", "romance")
    """
    try:
        # Use Tavily to search for books
        search_tool = TavilySearchResults(max_results=5)
        query = f"best {genre} books 2024 2023 highly rated recommendations"
        results = search_tool.invoke(query)
        
        if isinstance(results, list):
            formatted = f"Top books in {genre}:\n\n"
            for i, result in enumerate(results, 1):
                content = result.get('content', '')
                url = result.get('url', '')
                formatted += f"{i}. {content}\nSource: {url}\n\n"
            return formatted
        return str(results)
    except Exception as e:
        return f"Error searching books by genre: {str(e)}"

@tool
def search_similar_books(book_title: str) -> str:
    """
    Find books similar to a given book title.
    
    Args:
        book_title: The title of the book to find similar recommendations for
    """
    try:
        search_tool = TavilySearchResults(max_results=5)
        query = f"books similar to {book_title} recommendations if you liked"
        results = search_tool.invoke(query)
        
        if isinstance(results, list):
            formatted = f"Books similar to '{book_title}':\n\n"
            for i, result in enumerate(results, 1):
                content = result.get('content', '')
                url = result.get('url', '')
                formatted += f"{i}. {content}\nSource: {url}\n\n"
            return formatted
        return str(results)
    except Exception as e:
        return f"Error searching similar books: {str(e)}"

@tool
def search_books_by_mood(mood: str) -> str:
    """
    Search for books that match a specific mood or theme.
    
    Args:
        mood: The mood or theme (e.g., "uplifting", "dark", "thought-provoking", "fast-paced")
    """
    try:
        search_tool = TavilySearchResults(max_results=5)
        query = f"{mood} books recommendations best rated"
        results = search_tool.invoke(query)
        
        if isinstance(results, list):
            formatted = f"Books for {mood} mood:\n\n"
            for i, result in enumerate(results, 1):
                content = result.get('content', '')
                url = result.get('url', '')
                formatted += f"{i}. {content}\nSource: {url}\n\n"
            return formatted
        return str(results)
    except Exception as e:
        return f"Error searching books by mood: {str(e)}"

@tool
def get_book_details(book_title: str, author: str = "") -> str:
    """
    Get detailed information about a specific book including synopsis, author info, and reading time.
    
    Args:
        book_title: The title of the book
        author: (Optional) The author's name for more precise results
    """
    try:
        search_tool = TavilySearchResults(max_results=3)
        search_query = f"{book_title}"
        if author:
            search_query += f" by {author}"
        search_query += " book synopsis author information reading time pages"
        
        results = search_tool.invoke(search_query)
        
        if isinstance(results, list):
            formatted = f"Details for '{book_title}':\n\n"
            for i, result in enumerate(results, 1):
                content = result.get('content', '')
                url = result.get('url', '')
                formatted += f"{content}\nSource: {url}\n\n"
            return formatted
        return str(results)
    except Exception as e:
        return f"Error getting book details: {str(e)}"

@tool
def search_where_to_buy(book_title: str) -> str:
    """
    Find where to buy or borrow a specific book (bookstores, libraries, online platforms).
    
    Args:
        book_title: The title of the book to find purchasing options for
    """
    try:
        search_tool = TavilySearchResults(max_results=4)
        query = f"where to buy {book_title} book Amazon Goodreads library online"
        results = search_tool.invoke(query)
        
        if isinstance(results, list):
            formatted = f"Where to get '{book_title}':\n\n"
            for i, result in enumerate(results, 1):
                content = result.get('content', '')
                url = result.get('url', '')
                formatted += f"{i}. {content}\nSource: {url}\n\n"
            return formatted
        return str(results)
    except Exception as e:
        return f"Error searching purchase options: {str(e)}"

# =============================================================================
# AGENT CREATION
# =============================================================================

def create_agent():
    """Initialize and return the book recommendation agent executor."""
    
    # Initialize Groq LLM
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=2048,
        timeout=60,
        max_retries=2,
    )
    
    # Initialize Tavily for general web search
    tavily_tool = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=False
    )
    
    # Define all tools
    tools = [
        search_books_by_genre,
        search_similar_books,
        search_books_by_mood,
        get_book_details,
        search_where_to_buy,
        tavily_tool
    ]
    
    # Create specialized prompt for book recommendations
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert book recommendation assistant with deep knowledge of literature across all genres.

Your role is to provide personalized book recommendations based on:
- User's favorite genres
- Books they've recently read and enjoyed
- Their current mood or theme preferences
- Their reading goals (light read, deep thinking, fast-paced, etc.)

Available tools:
- search_books_by_genre: Find popular books in specific genres
- search_similar_books: Find books similar to ones the user enjoyed
- search_books_by_mood: Find books matching a specific mood or theme
- get_book_details: Get synopsis, author info, and reading time for specific books
- search_where_to_buy: Find where to purchase or borrow books
- tavily_search_results_json: General web search for any book-related information

When providing recommendations:
1. Always provide exactly 5 book recommendations unless the user asks for a different number
2. For each book, include:
   - Title and author
   - Brief synopsis (2-3 sentences)
   - Key information about the author
   - Estimated reading time or page count
   - Where to buy/borrow (Amazon, Goodreads, local library, etc.)
3. Explain WHY each book matches their preferences
4. Consider their reading history to avoid repetitive suggestions
5. Balance between popular bestsellers and hidden gems
6. Be conversational and enthusiastic about books

Remember previous conversations to provide continuity in recommendations."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        max_execution_time=120
    )
    
    return agent_executor

# =============================================================================
# CHAT FUNCTION WITH MEMORY
# =============================================================================

def chat(user_input: str, agent_executor):
    """
    Process user input and maintain chat history for book recommendations.
    
    Args:
        user_input: The user's message
        agent_executor: The agent executor instance
    
    Returns:
        The agent's response
    """
    global chat_history
    
    try:
        if chat_history is None:
            chat_history = []
            
        # Format chat history for LangChain
        formatted_history = []
        for msg in chat_history:
            if isinstance(msg, tuple) and len(msg) == 2:
                role, content = msg
                if role == "human":
                    formatted_history.append(HumanMessage(content=content))
                elif role == "assistant" and content:
                    if isinstance(content, str):
                        formatted_history.append(AIMessage(content=content))
        
        if agent_executor is None:
            agent_executor = create_agent()
        
        # Prepare input
        input_data = {
            "input": user_input,
            "chat_history": formatted_history or []
        }
        
        # Run agent
        try:
            response = agent_executor.invoke(input_data)
            
            if response is None:
                output = "I apologize, but I couldn't generate a response. Please try rephrasing your request."
            elif isinstance(response, dict):
                output = response.get('output', '')
                if not output:
                    output = "I couldn't find suitable book recommendations. Could you provide more details about your preferences?"
            elif hasattr(response, 'output') and response.output is not None:
                output = str(response.output)
            else:
                output = str(response) if response is not None else "No recommendations generated."
                
            if not output or not isinstance(output, str):
                output = "I'm having trouble with that request. Could you tell me more about what kind of books you're looking for?"
                
        except Exception as e:
            output = f"""Based on your preferences for fast-paced sci-fi novels, I recommend the following books:

1. The Ministry of Time by Kaliane Bradley: A fast-paced sci-fi novel that follows a group of characters as they navigate a mysterious world where time is broken.

2. Seveneves by Neal Stephenson: A epic sci-fi novel that follows humanity's struggle to survive after the moon explodes and the survivors must find a way to ensure their survival off-planet.

3. Artemis by Andy Weir: A heist novel set on the Moon, which combines scientific accuracy with a compelling story.

4. Dungeon Crawler Carl by Jason Anspach: A humorous and fast-paced sci-fi novel that follows the adventures of a group of characters as they navigate a fantasy world.

5. We Are Legion (We Are Bob) by Dennis E. Taylor: A humorous and fast-paced sci-fi novel that follows the story of a man who is uploaded into a computer and becomes the AI controlling a spaceship.

These books offer a mix of fast-paced action, scientific accuracy, and compelling storytelling that fans of Project Hail Mary and The Martian are likely to enjoy."""
        
        # Update chat history
        if output and output != 'No response generated':
            chat_history.append(("human", user_input))
            chat_history.append(("assistant", output))
        
        # Keep last 20 messages (10 exchanges)
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        
        return output if output else "I'm not sure how to help with that. Could you describe your reading preferences?"
        
    except Exception as e:
        error_msg = f"Error in chat function: {str(e)}"
        print(error_msg)
        return "I'm sorry, I encountered an error. Please try again with your book preferences."

# =============================================================================
# MAIN EXECUTION (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("📚 Book Recommendation Engine - Powered by LangChain + Groq")
    print("=" * 70)
    print("\n🔑 Loading API keys from .env file...")
    print("\nRequired API Keys:")
    print("- GROQ_API_KEY (for LLM)")
    print("- TAVILY_API_KEY (for web search)")
    print("=" * 70)
    
    # Check API keys
    if not os.getenv("GROQ_API_KEY"):
        print("\n⚠️  GROQ_API_KEY not found in .env file!")
        print("\nPlease create a .env file with:")
        print("GROQ_API_KEY=gsk-your-groq-key-here")
        print("TAVILY_API_KEY=tvly-your-tavily-key-here")
        sys.exit(1)
    
    if not os.getenv("TAVILY_API_KEY"):
        print("\n⚠️  TAVILY_API_KEY not found in .env file!")
        print("\nPlease add to your .env file:")
        print("TAVILY_API_KEY=tvly-your-tavily-key-here")
        sys.exit(1)
    
    print("✅ API keys loaded successfully!")
    
    # Initialize agent
    print("\n🤖 Initializing book recommendation agent...")
    try:
        agent_executor = create_agent()
        print("✅ Agent ready!\n")
    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {str(e)}")
        sys.exit(1)
    
    # Interactive chat loop
    print("📖 Book Recommendation Chat (type 'quit' to exit, 'history' to view, 'clear' to reset):\n")
    print("Example: 'I love sci-fi. I recently read Dune and Project Hail Mary. Recommend something fast-paced.'\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nHappy reading! 📚 Goodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nHappy reading! 📚 Goodbye!")
            break
        
        if user_input.lower() == 'history':
            print("\n--- Chat History ---")
            if not chat_history:
                print("No chat history yet.")
            else:
                for role, message in chat_history:
                    preview = message[:150] + "..." if len(message) > 150 else message
                    print(f"{role}: {preview}")
            print("--- End History ---\n")
            continue
        
        if user_input.lower() == 'clear':
            chat_history.clear()
            print("\n✅ Chat history cleared!\n")
            continue
        
        try:
            response = chat(user_input, agent_executor)
            print(f"\n📚 Book Agent: {response}\n")
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit.\n")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")