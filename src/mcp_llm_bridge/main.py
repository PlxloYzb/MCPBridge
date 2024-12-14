# src/mcp_llm_bridge/main.py
import os
import asyncio
from dotenv import load_dotenv
from mcp import StdioServerParameters
from mcp_llm_bridge.config import BridgeConfig, LLMConfig
from mcp_llm_bridge.bridge import BridgeManager
import colorlog
import logging

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s%(reset)s:     %(cyan)s%(name)s%(reset)s - %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

async def main():
    # Load environment variables
    load_dotenv()

    # Get the project root directory (where test.db is located)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(project_root, "test.db")
    
    # Define paths for PDF processing
    template_path = os.path.join(project_root, "tests", "template.pdf")
    output_dir = os.path.join(project_root, "tests", "filled")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure bridge
    config = BridgeConfig(
        mcp_server_params=StdioServerParameters(
            command="uvx",
            args=["mcp-server-sqlite", "--db-path", db_path],
            env=None
        ),
        llm_config=LLMConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            base_url=None
        ),
        system_prompt=f"""You are a helpful assistant that can use tools to help answer questions.
You can:
1. Query the database using SQL
2. Fill PDF forms by specifying coordinates and text

For PDF operations, you'll need:
- Template path: {template_path}
- Output directory: {output_dir}
- Coordinates (x, y) for each text field
- The text content to fill"""
    )
    
    logger.info(f"Starting bridge with model: {config.llm_config.model}")
    logger.info(f"Using database at: {db_path}")
    
    # Use bridge with context manager
    async with BridgeManager(config) as bridge:
        while True:
            try:
                user_input = input("\nEnter your prompt (or 'quit' to exit): ")
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                response = await bridge.process_message(user_input)
                print(f"\nResponse: {response}")
                
            except KeyboardInterrupt:
                logger.info("\nExiting...")
                break
            except Exception as e:
                logger.error(f"\nError occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())