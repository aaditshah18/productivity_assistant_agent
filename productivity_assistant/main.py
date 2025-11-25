import gradio as gr
import asyncio
from productivity_assistant.mcp_agent import MCPAgent
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize agent
agent = MCPAgent()
asyncio.run(agent.initialize())

def chat(message, history):
    """Process chat message and return response."""
    response = agent.chat(message)
    return response

# Create Gradio interface
demo = gr.ChatInterface(
    fn=chat,
    title="🤖 Productivity Assistant",
    description="Your AI-powered assistant for managing emails and calendar. Powered by Claude and MCP.",
    examples=[
        "📧 Check my last 3 emails",
        "📅 What's on my calendar today?",
        "🔍 Find emails from Gymshark",
        "📝 Create a meeting for tomorrow at 2pm",
        "🗓️ Show me my events this week"
    ],
    chatbot=gr.Chatbot(
        height=500,
        avatar_images=(
            "https://api.dicebear.com/9.x/lorelei/svg?seed=aadit",
            "https://api.dicebear.com/7.x/bottts/svg?seed=assistant"
        )
    ),
)

if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        show_error=True,
    )