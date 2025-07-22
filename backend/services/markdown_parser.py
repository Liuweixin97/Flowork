import re
import markdown
from typing import Dict, List, Any

class ResumeMarkdownParser:
    """简历Markdown解析器，将Markdown格式的简历解析为结构化数据"""
    
    def __init__(self):
        self.md = markdown.Markdown(extensions=['extra', 'codehilite'])
    
    def parse(self, markdown_text: str) -> Dict[str, Any]:
        """解析Markdown简历为结构化数据"""
        
        # 清理和预处理
        markdown_text = markdown_text.strip()
        
        # 基本信息提取
        resume_data = {
            'personal_info': self._extract_personal_info(markdown_text),
            'sections': self._extract_sections(markdown_text),
            'raw_markdown': markdown_text
        }
        
        return resume_data
    
    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """提取个人基本信息"""
        info = {}
        
        # 提取姓名 (通常是第一个H1标题)
        name_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        if name_match:
            info['name'] = name_match.group(1).strip()
        
        # 提取联系方式
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_match:
            info['email'] = email_match.group(1)
        
        phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', text)
        if phone_match:
            info['phone'] = phone_match.group(1).strip()
        
        # 提取地址
        address_patterns = [
            r'地址[:：]\s*(.+)',
            r'住址[:：]\s*(.+)',
            r'现居[:：]\s*(.+)'
        ]
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                info['address'] = match.group(1).strip()
                break
        
        return info
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """提取简历各个部分"""
        sections = []
        
        # 按H2标题分割内容
        h2_pattern = r'^##\s+(.+)$'
        parts = re.split(h2_pattern, text, flags=re.MULTILINE)
        
        # 第一部分通常是个人信息，跳过
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                title = parts[i].strip()
                content = parts[i + 1].strip()
                
                section = {
                    'title': title,
                    'content': content,
                    'type': self._classify_section_type(title),
                    'items': self._extract_section_items(content, title)
                }
                sections.append(section)
        
        return sections
    
    def _classify_section_type(self, title: str) -> str:
        """分类部分类型"""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['教育', '学历', 'education']):
            return 'education'
        elif any(keyword in title_lower for keyword in ['工作', '经历', '职业', 'experience', 'work']):
            return 'experience'
        elif any(keyword in title_lower for keyword in ['技能', 'skills', '专业技能']):
            return 'skills'
        elif any(keyword in title_lower for keyword in ['项目', 'projects', '项目经验']):
            return 'projects'
        elif any(keyword in title_lower for keyword in ['证书', '认证', 'certificates']):
            return 'certificates'
        else:
            return 'other'
    
    def _extract_section_items(self, content: str, section_title: str) -> List[Dict[str, Any]]:
        """提取部分中的条目"""
        items = []
        
        # 按列表项或段落分割
        if '-' in content or '*' in content:
            # 列表格式
            list_items = re.findall(r'^[-*]\s+(.+)$', content, re.MULTILINE)
            for item in list_items:
                items.append({
                    'type': 'list_item',
                    'content': item.strip()
                })
        else:
            # 段落格式，按双换行分割
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for paragraph in paragraphs:
                items.append({
                    'type': 'paragraph',
                    'content': paragraph
                })
        
        return items

    def markdown_to_html(self, markdown_text: str) -> str:
        """将Markdown转换为HTML"""
        return self.md.convert(markdown_text)