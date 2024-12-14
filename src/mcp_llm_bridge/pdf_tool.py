import os
from typing import Dict, Any
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

class PDFTool:
    def __init__(self, template_path: str, output_dir: str):
        """
        初始化PDF工具
        :param template_path: 模板PDF文件路径
        :param output_dir: 填充后PDF的输出目录
        """
        self.template_path = template_path
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def fill_pdf(self, coordinates: Dict[str, Dict[str, Any]], output_filename: str) -> str:
        """
        在PDF中填充文本
        :param coordinates: 坐标和文本内容的字典，格式如：
                          {"field1": {"x": 100, "y": 100, "text": "content"}}
        :param output_filename: 输出文件名
        :return: 填充后的PDF文件路径
        """
        # 读取模板PDF
        template_pdf = PdfReader(open(self.template_path, "rb"))
        output = PdfWriter()

        # 获取第一页
        template_page = template_pdf.pages[0]
        page_width = float(template_page.mediabox.width)
        page_height = float(template_page.mediabox.height)

        # 创建一个临时的PDF文件用于绘制文本
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # 在坐标位置添加文本
        for field, props in coordinates.items():
            x = props["x"]
            y = props["y"]
            text = props["text"]
            can.drawString(x, y, text)

        can.save()
        packet.seek(0)
        
        # 创建新的PDF，包含文本
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]

        # 合并模板和文本
        template_page.merge_page(new_page)
        output.add_page(template_page)

        # 保存结果
        output_path = os.path.join(self.output_dir, output_filename)
        with open(output_path, "wb") as output_file:
            output.write(output_file)

        return output_path
