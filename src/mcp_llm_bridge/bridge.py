from typing import Optional, List, Dict, Any
import logging
import os
from .config import BridgeConfig
from .tools import DatabaseQueryTool
import re

class MCPLLMBridge:
    """Bridge class for handling LLM interactions"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.tool = None
        
    async def initialize(self):
        """Initialize the bridge"""
        try:
            self.tool = DatabaseQueryTool("test.db")
            logging.info("Bridge initialized successfully")
        except Exception as e:
            logging.error(f"Bridge initialization failed: {str(e)}")
            raise
            
    async def process_message(self, message: str) -> str:
        """Process incoming message and return response"""
        if "pdf" in message.lower():
            # Extract coordinates and text from message using regex
            coordinates = {}
            pattern = r'坐标\((\d+),(\d+)\)处填入"([^"]+)"'
            matches = re.finditer(pattern, message)
            
            for i, match in enumerate(matches):
                x, y, text = match.groups()
                coordinates[f"field{i}"] = {
                    "x": int(x),
                    "y": int(y),
                    "text": text
                }
                
            if coordinates:
                # Setup paths
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                template_path = os.path.join(project_root, "tests", "template.pdf")
                output_dir = os.path.join(project_root, "tests", "filled")
                output_path = os.path.join(output_dir, "filled_form.pdf")
                
                # Ensure output directory exists
                os.makedirs(output_dir, exist_ok=True)
                
                # Fill PDF
                try:
                    self.tool.fill_pdf(template_path, output_path, coordinates)
                    return f"PDF已生成，保存在: {output_path}"
                except Exception as e:
                    return f"PDF生成失败: {str(e)}"
            
        # Default to database query
        try:
            results = self.tool.execute_query(message)
            return str(results)
        except Exception as e:
            return f"查询执行失败: {str(e)}"
            
    async def close(self):
        """Close the bridge"""
        pass


class BridgeManager:
    """Manager class for handling the bridge lifecycle"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.bridge: Optional[MCPLLMBridge] = None
        
    async def __aenter__(self) -> MCPLLMBridge:
        """Context manager entry"""
        self.bridge = MCPLLMBridge(self.config)
        await self.bridge.initialize()
        return self.bridge
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.bridge:
            await self.bridge.close()