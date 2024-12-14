from typing import Dict, List, Any
from dataclasses import dataclass
import sqlite3
import logging
from .pdf_tool import PDFTool
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

@dataclass
class DatabaseSchema:
    """Represents the schema of a database table"""
    table_name: str
    columns: Dict[str, str]
    description: str

class DatabaseQueryTool:
    """Tool for executing database queries with schema validation"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.schemas: Dict[str, DatabaseSchema] = {}
        
        # Register default product schema
        self.register_schema(DatabaseSchema(
            table_name="products",
            columns={
                "id": "INTEGER",
                "title": "TEXT",
                "description": "TEXT",
                "price": "REAL",
                "category": "TEXT",
                "stock": "INTEGER",
                "created_at": "DATETIME"
            },
            description="Product catalog with items for sale"
        ))
    
    def register_schema(self, schema: DatabaseSchema):
        """Register a database schema"""
        self.schemas[schema.table_name] = schema
    
    def get_tool_spec(self) -> Dict[str, Any]:
        """Get the tool specification in MCP format"""
        schema_desc = "\n".join([
            f"Table {schema.table_name}: {schema.description}\n"
            f"Columns: {', '.join(f'{name} ({type_})' for name, type_ in schema.columns.items())}"
            for schema in self.schemas.values()
        ])
        
        return {
            "name": "query_database",
            "description": f"Execute SQL queries against the database. Available schemas:\n{schema_desc}",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        }
    
    def get_schema_description(self) -> str:
        """Get a formatted description of all registered schemas"""
        schema_parts = []
        for schema in self.schemas.values():
            column_info = []
            for name, type_ in schema.columns.items():
                column_info.append(f"  - {name} ({type_})")
            schema_parts.append(f"Table {schema.table_name}: {schema.description}\n" + "\n".join(column_info))
            
        return "\n\n".join(schema_parts)
    
    def validate_query(self, query: str) -> bool:
        """Validate a query against registered schemas"""
        query = query.lower()
        for schema in self.schemas.values():
            if schema.table_name in query:
                # Check if query references any non-existent columns
                for word in query.split():
                    if '.' in word:
                        table, column = word.split('.')
                        if table == schema.table_name and column not in schema.columns:
                            return False
        return True
    
    async def execute(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        query = params.get("query")
        if not query:
            raise ValueError("Query parameter is required")
            
        if not self.validate_query(query):
            raise ValueError("Query references invalid columns")
            
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        finally:
            conn.close()
            
    def get_db_schema_description(self) -> str:
        """Get database schema description"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema_desc = []
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                # Format column information
                column_desc = [f"  - {col[1]} ({col[2]})" for col in columns]
                schema_desc.append(f"Table: {table_name}\n" + "\n".join(column_desc))
            
            return "\n\n".join(schema_desc)
            
        finally:
            conn.close()
            
    def execute_db_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Format results as list of dictionaries
            return [dict(zip(column_names, row)) for row in results]
            
        finally:
            conn.close()

    def fill_pdf(self, template_path: str, output_path: str, coordinates: Dict[str, Dict[str, Any]]) -> str:
        """Fill PDF with text at specified coordinates"""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Read template PDF
        template_pdf = PdfReader(open(template_path, "rb"))
        output = PdfWriter()

        # Get first page
        template_page = template_pdf.pages[0]
        page_width = float(template_page.mediabox.width)
        page_height = float(template_page.mediabox.height)

        # Create temporary PDF for drawing text
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # Add text at coordinates
        for field, props in coordinates.items():
            x = props["x"]
            y = props["y"]
            text = props["text"]
            can.drawString(x, y, text)

        can.save()
        packet.seek(0)
        
        # Create new PDF with text
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]

        # Merge template and text
        template_page.merge_page(new_page)
        output.add_page(template_page)

        # Save result
        with open(output_path, "wb") as output_file:
            output.write(output_file)

        return output_path

class CombinedTool:
    """Combined tool for database queries and PDF operations"""
    
    def __init__(self, db_path: str, template_path: str, output_dir: str):
        self.db_tool = DatabaseQueryTool(db_path)
        self.pdf_tool = PDFTool(template_path, output_dir)
        
    def get_schema_description(self) -> str:
        return self.db_tool.get_db_schema_description()
        
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        return self.db_tool.execute_db_query(query)
        
    def fill_pdf(self, coordinates: Dict[str, Dict[str, Any]], output_filename: str) -> str:
        return self.pdf_tool.fill_pdf(coordinates, output_filename)