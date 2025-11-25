import logging
from productivity_assistant.mcp_client import MCPClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set default level, can be overridden by main config

class AssistantAgent:
    def __init__(self):
        self.mcp_client = MCPClient()
        
    def run(self, user_message: str) -> str:
        """
        Sends the user's natural language message to Claude,
        which then orchestrates tool calls via MCPClient.
        """
        logger.info(f"User message received: '{user_message}'")
        response = self.mcp_client.direct_chat_with_claude(user_message)
        logger.info(f"Claude's response: '{response}'")
        return response

if __name__ == "__main__":
    agent = AssistantAgent()
    logger.info("Agent setup complete. To run, ensure .env is configured.")
    logger.info("This agent now directly sends messages to Claude for tool orchestration.")