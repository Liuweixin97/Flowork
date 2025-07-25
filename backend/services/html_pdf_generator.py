"""
HTML转PDF生成器
使用markdown转HTML，再转PDF的方式
"""

import markdown
from markdown.extensions import codehilite, tables, toc
import os
import tempfile
from typing import Dict, Any
import subprocess
import platform

class HTMLPDFGenerator:
    """基于HTML的PDF生成器"""
    
    def __init__(self):
        # 配置markdown扩展
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.extra',  # 包含tables, fenced_code等
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br',  # 换行转br
                'markdown.extensions.attr_list'  # 属性列表
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False
                }
            }
        )
        
        # 检查wkhtmltopdf是否可用
        self.wkhtmltopdf_available = self._check_wkhtmltopdf()
        
    def _check_wkhtmltopdf(self) -> bool:
        """检查wkhtmltopdf是否安装"""
        try:
            result = subprocess.run(['wkhtmltopdf', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _generate_html_content(self, resume_data: Dict[str, Any]) -> str:
        """将简历数据转换为HTML"""
        # 提取个人信息
        personal_info = resume_data.get('personal_info', {})
        name = personal_info.get('name', '简历')
        email = personal_info.get('email', '')
        phone = personal_info.get('phone', '')
        address = personal_info.get('address', '')
        
        # 构建完整的markdown内容
        markdown_content = f"# {name}\n\n"
        
        # 添加联系信息
        contact_info = []
        if email:
            contact_info.append(f"📧 {email}")
        if phone:
            contact_info.append(f"📱 {phone}")
        if address:
            contact_info.append(f"📍 {address}")
        
        if contact_info:
            markdown_content += " | ".join(contact_info) + "\n\n"
            markdown_content += "---\n\n"
        
        # 添加各个章节
        sections = resume_data.get('sections', [])
        for section in sections:
            section_title = section.get('title', '')
            if section_title:
                markdown_content += f"## {section_title}\n\n"
            
            items = section.get('items', [])
            for item in items:
                content = item.get('content', '')
                if content:
                    item_type = item.get('type', 'text')
                    
                    if item_type == 'list_item':
                        # 列表项
                        markdown_content += f"- {content}\n"
                    else:
                        # 段落内容
                        markdown_content += f"{content}\n\n"
            
            markdown_content += "\n"
        
        # 将markdown转换为HTML
        html_body = self.md.convert(markdown_content)
        
        # 构建完整的HTML文档
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm 1.5cm;
            @bottom-center {{
                content: counter(page) "/" counter(pages);
                font-size: 10px;
                color: #666;
            }}
        }}
        
        body {{
            font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
            margin: 0;
            padding: 0;
            font-size: 12px;
        }}
        
        h1 {{
            color: #1a1a1a;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin: 0 0 10px 0;
            padding: 0;
        }}
        
        h2 {{
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #3498db;
        }}
        
        h3 {{
            color: #2c3e50;
            font-size: 14px;
            font-weight: 600;
            margin: 15px 0 8px 0;
        }}
        
        p {{
            margin: 6px 0;
            line-height: 1.5;
        }}
        
        ul, ol {{
            margin: 8px 0 8px 20px;
            padding: 0;
        }}
        
        li {{
            margin: 3px 0;
            line-height: 1.4;
        }}
        
        strong {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        em {{
            font-style: italic;
            color: #5d6d7e;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 11px;
        }}
        
        /* 联系信息样式 */
        p:first-of-type {{
            text-align: center;
            font-size: 11px;
            color: #666;
            margin: 0 0 15px 0;
        }}
        
        /* 分隔线样式 */
        hr {{
            border: none;
            height: 1px;
            background-color: #e1e8ed;
            margin: 15px 0;
        }}
        
        /* 表格样式（如果有） */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        
        td, th {{
            padding: 6px 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            font-size: 11px;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        
        /* 打印优化 */
        @media print {{
            body {{
                font-size: 11px;
            }}
            
            h1 {{
                font-size: 24px;
            }}
            
            h2 {{
                font-size: 14px;
                page-break-after: avoid;
            }}
            
            h3 {{
                font-size: 12px;
                page-break-after: avoid;
            }}
            
            p, li {{
                page-break-inside: avoid;
                orphans: 2;
                widows: 2;
            }}
            
            ul, ol {{
                page-break-inside: avoid;
            }}
        }}
        
        /* 智能一页优化 */
        .smart-onepage {{
            font-size: 10px;
        }}
        
        .smart-onepage h1 {{
            font-size: 20px;
            margin-bottom: 8px;
        }}
        
        .smart-onepage h2 {{
            font-size: 13px;
            margin: 12px 0 6px 0;
        }}
        
        .smart-onepage h3 {{
            font-size: 11px;
            margin: 8px 0 4px 0;
        }}
        
        .smart-onepage p {{
            margin: 3px 0;
            line-height: 1.3;
        }}
        
        .smart-onepage li {{
            margin: 1px 0;
            line-height: 1.3;
        }}
    </style>
</head>
<body{body_class}>
{content}
</body>
</html>
        """.strip()
        
        # 根据smart_onepage参数决定是否添加class
        body_class = ' class="smart-onepage"' if hasattr(self, '_smart_onepage') and self._smart_onepage else ''
        
        return html_template.format(
            title=name,
            content=html_body,
            body_class=body_class
        )
    
    def generate_pdf_with_wkhtmltopdf(self, html_content: str, smart_onepage: bool = False) -> bytes:
        """使用wkhtmltopdf生成PDF"""
        if not self.wkhtmltopdf_available:
            raise RuntimeError("wkhtmltopdf 未安装或不可用")
        
        # 创建临时HTML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as html_file:
            html_file.write(html_content)
            html_file_path = html_file.name
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(mode='rb', suffix='.pdf', delete=False) as pdf_file:
            pdf_file_path = pdf_file.name
        
        try:
            # wkhtmltopdf命令选项
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '15mm' if smart_onepage else '20mm',
                '--margin-bottom', '15mm' if smart_onepage else '20mm',  
                '--margin-left', '12mm' if smart_onepage else '15mm',
                '--margin-right', '12mm' if smart_onepage else '15mm',
                '--encoding', 'UTF-8',
                '--print-media-type',
                '--no-background',
                '--enable-local-file-access',
            ]
            
            if smart_onepage:
                # 智能一页优化选项
                cmd.extend([
                    '--zoom', '0.9',  # 稍微缩小以适应更多内容
                    '--dpi', '150',   # 提高DPI保持清晰度
                ])
            
            cmd.extend([html_file_path, pdf_file_path])
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise RuntimeError(f"wkhtmltopdf 执行失败: {result.stderr}")
            
            # 读取生成的PDF
            with open(pdf_file_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            return pdf_data
            
        finally:
            # 清理临时文件
            try:
                os.unlink(html_file_path)
                os.unlink(pdf_file_path)
            except OSError:
                pass
    
    def generate_pdf_with_playwright(self, html_content: str, smart_onepage: bool = False) -> bytes:
        """使用Playwright生成PDF（备用方案）"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise RuntimeError("Playwright 未安装，请运行: pip install playwright && playwright install chromium")
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 设置页面内容
            page.set_content(html_content)
            
            # PDF选项
            pdf_options = {
                'format': 'A4',
                'margin': {
                    'top': '15mm' if smart_onepage else '20mm',
                    'bottom': '15mm' if smart_onepage else '20mm', 
                    'left': '12mm' if smart_onepage else '15mm',
                    'right': '12mm' if smart_onepage else '15mm'
                },
                'print_background': True,
                'prefer_css_page_size': True
            }
            
            if smart_onepage:
                # 智能一页模式：尝试缩放以适应一页
                pdf_options['scale'] = 0.85
            
            # 生成PDF
            pdf_data = page.pdf(**pdf_options)
            
            browser.close()
            return pdf_data
    
    def generate_pdf(self, resume_data: Dict[str, Any], smart_onepage: bool = False) -> bytes:
        """生成PDF简历"""
        # 设置智能一页模式标记
        self._smart_onepage = smart_onepage
        
        # 生成HTML内容
        html_content = self._generate_html_content(resume_data)
        
        # 尝试使用wkhtmltopdf生成PDF
        if self.wkhtmltopdf_available:
            print("使用 wkhtmltopdf 生成PDF")
            return self.generate_pdf_with_wkhtmltopdf(html_content, smart_onepage)
        else:
            # 备用：尝试使用Playwright
            try:
                print("使用 Playwright 生成PDF")
                return self.generate_pdf_with_playwright(html_content, smart_onepage)
            except RuntimeError as e:
                # 如果都不可用，返回错误信息
                raise RuntimeError(f"无法生成PDF: wkhtmltopdf和Playwright都不可用。错误: {str(e)}")
    
    def get_html_content(self, resume_data: Dict[str, Any], smart_onepage: bool = False) -> str:
        """获取HTML内容（用于预览或调试）"""
        self._smart_onepage = smart_onepage
        return self._generate_html_content(resume_data)