import asyncio
import os
import logging
from productivity_assistant.mcp_client import MCPClient # Import the renamed class
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def main():
    """Main function to run the agent."""
    
    # Centralized environment variable checks
    required_env_vars = {
        "ANTHROPIC_API_KEY": "Anthropic API Key",
        "GOOGLE_API_CLIENT_SECRET_FILE": "Google API client_secret.json path",
    }

    missing_env_vars = []
    for var, description in required_env_vars.items():
        if not os.getenv(var):
            missing_env_vars.append(description)
    
    if missing_env_vars:
        logging.error(f"Missing environment variables. Please set the following in your .env file:")
        for desc in missing_env_vars:
            logging.error(f"- {desc}")
        logging.error(f"Example .env file:")
        logging.error(f"""
# Anthropic API Key
ANTHROPIC_API_KEY=sk-...
# Google API client_secret.json path
GOOGLE_API_CLIENT_SECRET_FILE=./client_secret.json
""")
        return

    agent = MCPClient() # Instantiate MCPClient
    
    try:
        # Initialize MCP servers
        await agent.initialize()
        
        if not agent.mcp_sessions:
            print("\n❌ No MCP servers initialized. Please check your server configurations.")
            return
        
        print("\n" + "="*60)
        print("MCP Agent Ready! Type 'quit' to exit.")
        print("="*60 + "\n")
        
        # Interactive chat loop
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            print("\nClaude: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response)
            print()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanup
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
