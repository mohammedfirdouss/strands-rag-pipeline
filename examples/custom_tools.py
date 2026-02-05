"""
Example: Custom Tool Integration
Demonstrates how to create and integrate custom tools with the RAG agent.
"""

from typing import Dict, Any
from strands import Agent, tool
from strands_tools import calculator


# Define a custom tool
@tool
def weather_lookup(city: str) -> str:
    """Look up current weather for a city.
    
    Args:
        city: Name of the city
        
    Returns:
        Weather information for the city
    """
    # This is a mock implementation
    # In production, you would call a real weather API
    weather_data = {
        "Seattle": "Rainy, 55°F",
        "San Francisco": "Foggy, 62°F",
        "New York": "Cloudy, 48°F",
        "Miami": "Sunny, 82°F",
    }
    
    return weather_data.get(city, f"Weather data not available for {city}")


@tool
def database_query(query: str) -> str:
    """Query a mock database.
    
    Args:
        query: SQL-like query string
        
    Returns:
        Query results
    """
    # Mock database responses
    if "users" in query.lower():
        return "Found 150 users in the database"
    elif "products" in query.lower():
        return "Found 42 products in the database"
    else:
        return "Query executed successfully, 0 results"


def main():
    """Run custom tool integration example."""
    print("=" * 60)
    print("Custom Tool Integration Example")
    print("=" * 60)
    
    try:
        # Create agent with custom tools
        print("\n1. Creating agent with custom tools...")
        agent = Agent(
            tools=[weather_lookup, database_query, calculator],
            system_prompt="""You are a helpful assistant with access to weather information, 
            database queries, and a calculator. Use these tools to help answer user questions."""
        )
        print("✅ Agent created with custom tools!")
        
        # Example queries
        queries = [
            "What's the weather like in Seattle?",
            "How many users are in the database?",
            "What's 25 * 47?",
        ]
        
        print("\n2. Running example queries with custom tools...\n")
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'=' * 60}")
            print(f"Query {i}: {query}")
            print("-" * 60)
            
            try:
                response = agent(query)
                print(f"Response: {response}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print(f"\n{'=' * 60}")
        print("✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create agent: {str(e)}")
        print("\n💡 Make sure you have:")
        print("   1. Installed dependencies: pip install strands-agents strands-agents-tools")
        print("   2. Set up API keys in .env file")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
