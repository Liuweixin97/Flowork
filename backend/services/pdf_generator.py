from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor, black, grey, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from typing import Dict, Any, Tuple
import io
import re
import os
import math

class ResumePDFGenerator:
    """简历PDF生成器 - 使用ReportLab"""
    
    def __init__(self):
        # 注册HarmonyOS Sans中文字体
        self.chinese_font = 'Helvetica'  # 默认字体
        self.chinese_bold_font = 'Helvetica-Bold'
        self.chinese_medium_font = 'Helvetica-Bold'
        
        # 尝试注册HarmonyOS Sans字体
        try:
            # 获取fonts目录的绝对路径
            fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')
            fonts_dir = os.path.abspath(fonts_dir)
            
            # HarmonyOS Sans简体中文字体路径
            harmony_fonts_dir = os.path.join(fonts_dir, 'HarmonyOS Sans', 'HarmonyOS_Sans_SC')
            
            # 定义字体文件映射
            font_files = {
                'regular': os.path.join(harmony_fonts_dir, 'HarmonyOS_Sans_SC_Regular.ttf'),
                'bold': os.path.join(harmony_fonts_dir, 'HarmonyOS_Sans_SC_Bold.ttf'),
                'medium': os.path.join(harmony_fonts_dir, 'HarmonyOS_Sans_SC_Medium.ttf'),
                'light': os.path.join(harmony_fonts_dir, 'HarmonyOS_Sans_SC_Light.ttf')
            }
            
            # 检查并注册HarmonyOS Sans字体
            fonts_registered = 0
            for weight, font_path in font_files.items():
                try:
                    if os.path.exists(font_path):
                        font_name = f'HarmonyOS-{weight.capitalize()}'
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        print(f"成功注册字体: {font_name} -> {font_path}")
                        fonts_registered += 1
                        
                        # 设置主要字体
                        if weight == 'regular':
                            self.chinese_font = font_name
                        elif weight == 'bold':
                            self.chinese_bold_font = font_name
                        elif weight == 'medium':
                            self.chinese_medium_font = font_name
                            
                except Exception as e:
                    print(f"注册字体失败 {weight}: {e}")
                    continue
            
            if fonts_registered > 0:
                print(f"HarmonyOS Sans 字体注册成功，共注册 {fonts_registered} 个字重")
                print(f"常规字体: {self.chinese_font}")
                print(f"粗体字体: {self.chinese_bold_font}")
                print(f"中等字体: {self.chinese_medium_font}")
            else:
                # 如果HarmonyOS Sans不可用，尝试备选字体
                self._register_fallback_fonts(fonts_dir)
                
        except Exception as e:
            print(f"HarmonyOS Sans字体注册过程出错: {e}")
            self._register_fallback_fonts(fonts_dir)
        
        print(f"最终使用字体 - 常规: {self.chinese_font}, 粗体: {self.chinese_bold_font}")
        
        # 创建样式 - 确保在字体注册后创建
        self.styles = getSampleStyleSheet()
        self._create_modern_styles()
        
        # A4页面配置
        self.page_width, self.page_height = A4
        self.default_margins = {'top': 50, 'bottom': 50, 'left': 60, 'right': 60}
        self.available_height = self.page_height - self.default_margins['top'] - self.default_margins['bottom']
        self.available_width = self.page_width - self.default_margins['left'] - self.default_margins['right']
    
    def _register_fallback_fonts(self, fonts_dir):
        """注册备选字体"""
        try:
            # 备选字体路径
            fallback_fonts = [
                (os.path.join(fonts_dir, 'SourceHanSansSC-Regular.otf'), 'SourceHanSans'),
                (os.path.join(fonts_dir, 'NotoSansCJKsc-Regular.otf'), 'NotoSans'),
                ('/System/Library/Fonts/PingFang.ttc', 'PingFang'),
            ]
            
            for font_path, font_name in fallback_fonts:
                try:
                    if os.path.exists(font_path):
                        print(f"尝试注册备选字体: {font_path}")
                        if font_path.endswith('.otf'):
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                        else:
                            pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
                        
                        self.chinese_font = font_name
                        self.chinese_bold_font = font_name  # 使用相同字体作为粗体
                        self.chinese_medium_font = font_name
                        print(f"成功注册备选字体: {font_name}")
                        return
                except Exception as e:
                    print(f"备选字体注册失败 {font_name}: {e}")
                    continue
            
            # 最后尝试CID字体
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
                self.chinese_font = 'HeiseiKakuGo-W5'
                self.chinese_bold_font = 'HeiseiKakuGo-W5'
                self.chinese_medium_font = 'HeiseiKakuGo-W5'
                print("使用CID字体: HeiseiKakuGo-W5")
            except:
                print("使用默认字体: Helvetica")
                
        except Exception as e:
            print(f"备选字体注册过程出错: {e}")
    
    def _create_modern_styles(self):
        """创建现代化样式"""
        # 主标题 - 姓名
        self.styles.add(ParagraphStyle(
            name='NameTitle',
            parent=self.styles['Title'],
            fontName=self.chinese_bold_font,
            fontSize=28,
            textColor=HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=8,
            leading=32
        ))
        
        # 联系信息
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=HexColor('#666666'),
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=20,
            leading=14
        ))
        
        # 章节标题
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontName=self.chinese_medium_font,
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=8,
            borderPadding=(0, 0, 8, 0),
            borderColor=HexColor('#3498db'),
            borderWidth=0,
            leading=18
        ))
        
        # 正文内容
        self.styles.add(ParagraphStyle(
            name='ModernBodyText',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=HexColor('#333333'),
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=4,
            leading=14,
            leftIndent=0
        ))
        
        # 工作经历标题
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontName=self.chinese_medium_font,
            fontSize=11,
            textColor=HexColor('#2c3e50'),
            spaceBefore=8,
            spaceAfter=2,
            leading=13
        ))
        
        # 公司和时间
        self.styles.add(ParagraphStyle(
            name='CompanyDate',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=HexColor('#7f8c8d'),
            spaceBefore=0,
            spaceAfter=4,
            leading=11
        ))
        
        # 列表项
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=HexColor('#444444'),
            leftIndent=12,
            bulletIndent=0,
            spaceBefore=2,
            spaceAfter=2,
            leading=12
        ))
        
        # 技能项
        self.styles.add(ParagraphStyle(
            name='SkillItem',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=HexColor('#444444'),
            spaceBefore=2,
            spaceAfter=2,
            leading=11
        ))
    
    def _analyze_content_requirements(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析简历内容，估算页面空间需求"""
        analysis = {
            'estimated_height': 0,
            'sections_count': 0,
            'total_items': 0,
            'header_height': 0,
            'content_height': 0,
            'requires_compression': False,
            'compression_ratio': 1.0
        }
        
        # 计算头部高度（姓名 + 联系信息 + 间距）
        header_height = 0
        personal_info = resume_data.get('personal_info', {})
        
        # 姓名标题高度
        if personal_info.get('name'):
            name_style = self.styles['NameTitle']
            header_height += name_style.fontSize + name_style.spaceAfter
        
        # 联系信息高度
        contact_items = []
        if personal_info.get('email'):
            contact_items.append(personal_info['email'])
        if personal_info.get('phone'):
            contact_items.append(personal_info['phone'])
        if personal_info.get('address'):
            contact_items.append(personal_info['address'])
        
        if contact_items:
            contact_style = self.styles['ContactInfo']
            header_height += contact_style.fontSize + contact_style.spaceAfter
        
        # 额外分隔间距
        header_height += 10
        
        analysis['header_height'] = header_height
        
        # 计算内容区域高度
        content_height = 0
        sections = resume_data.get('sections', [])
        analysis['sections_count'] = len(sections)
        
        for section in sections:
            # 章节标题高度
            section_title = section.get('title', '')
            if section_title:
                section_style = self.styles['SectionTitle']
                content_height += (section_style.spaceBefore + 
                                 section_style.fontSize + 
                                 section_style.spaceAfter)
                # 分隔线高度
                content_height += 8 + 8  # 线条上下间距
            
            # 章节内容高度
            items = section.get('items', [])
            analysis['total_items'] += len(items)
            
            section_type = section.get('type', 'other')
            
            for item in items:
                content = item.get('content', '')
                if content:
                    item_type = item.get('type', 'text')
                    
                    # 估算文本行数
                    clean_content = self._clean_markdown(content)
                    estimated_lines = self._estimate_text_lines(clean_content, self.available_width)
                    
                    if item_type == 'list_item':
                        # 列表项
                        bullet_style = self.styles['BulletPoint']
                        item_height = (bullet_style.leading * estimated_lines + 
                                     bullet_style.spaceBefore + bullet_style.spaceAfter)
                    elif '|' in clean_content and section_type in ['experience', 'education', 'projects']:
                        # 职位/教育标题
                        job_style = self.styles['JobTitle']
                        item_height = (job_style.leading * estimated_lines + 
                                     job_style.spaceBefore + job_style.spaceAfter)
                    else:
                        # 普通文本
                        body_style = self.styles['ModernBodyText']
                        item_height = (body_style.leading * estimated_lines + 
                                     body_style.spaceBefore + body_style.spaceAfter)
                    
                    content_height += item_height
            
            # 章节间距
            content_height += 12
        
        analysis['content_height'] = content_height
        analysis['estimated_height'] = header_height + content_height
        
        # 判断是否需要压缩
        if analysis['estimated_height'] > self.available_height:
            analysis['requires_compression'] = True
            analysis['compression_ratio'] = self.available_height / analysis['estimated_height']
        
        return analysis
    
    def _estimate_text_lines(self, text: str, available_width: float, font_size: int = 10) -> int:
        """估算文本需要的行数"""
        if not text:
            return 1
        
        # 简单估算：假设平均字符宽度为字号的0.6倍
        char_width = font_size * 0.6
        chars_per_line = int(available_width / char_width)
        
        # 按行分割处理
        lines = text.split('\n')
        total_lines = 0
        
        for line in lines:
            if len(line) <= chars_per_line:
                total_lines += 1
            else:
                # 需要换行
                total_lines += math.ceil(len(line) / chars_per_line)
        
        return max(1, total_lines)
    
    def _create_optimized_styles(self, compression_ratio: float):
        """根据压缩比例创建优化的样式"""
        # 确保压缩比例在合理范围内
        compression_ratio = max(0.55, min(1.0, compression_ratio))
        
        # 更激进的压缩策略
        if compression_ratio < 0.75:
            # 需要大幅压缩
            font_scale = max(0.75, compression_ratio + 0.05)  # 更激进的字号缩放
            spacing_scale = max(0.45, compression_ratio * 0.8)  # 更激进的间距缩放
            header_font_scale = max(0.65, compression_ratio * 0.85)  # 头部字号单独更激进缩放
        else:
            # 中等压缩或微调
            font_scale = max(0.85, min(0.95, compression_ratio))  # 修正：不应该超过原尺寸
            spacing_scale = max(0.6, compression_ratio * 0.9)
            header_font_scale = max(0.8, min(0.95, compression_ratio))
        
        print(f"智能一页优化 - 字号缩放: {font_scale:.2f}, 间距缩放: {spacing_scale:.2f}, 头部字号缩放: {header_font_scale:.2f}")
        
        # 创建优化的样式
        optimized_styles = getSampleStyleSheet()
        
        # 主标题 - 姓名（更激进的压缩）
        name_font_size = max(18, int(28 * header_font_scale))  # 最小18pt
        optimized_styles.add(ParagraphStyle(
            name='NameTitle',
            parent=optimized_styles['Title'],
            fontName=self.chinese_bold_font,
            fontSize=name_font_size,
            textColor=HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=max(2, int(6 * spacing_scale)),  # 减少间距
            leading=max(20, int(name_font_size * 1.1))  # 更紧凑的行间距
        ))
        
        # 联系信息（更紧凑）
        contact_font_size = max(8, int(10 * font_scale))  # 最小8pt
        optimized_styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=optimized_styles['Normal'],
            fontName=self.chinese_font,
            fontSize=contact_font_size,
            textColor=HexColor('#666666'),
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=max(4, int(12 * spacing_scale)),  # 大幅减少间距
            leading=max(10, int(contact_font_size * 1.2))
        ))
        
        # 章节标题（在智能一页模式下更激进压缩）
        section_font_size = max(12, int(14 * font_scale))  # 最小12pt
        optimized_styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=optimized_styles['Heading1'],
            fontName=self.chinese_medium_font,
            fontSize=section_font_size,
            textColor=HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceBefore=max(8, int(16 * spacing_scale)),  # 减少上间距
            spaceAfter=max(4, int(6 * spacing_scale)),     # 减少下间距
            borderPadding=(0, 0, 8, 0),
            borderColor=HexColor('#3498db'),
            borderWidth=0,
            leading=max(14, int(section_font_size * 1.1))
        ))
        
        # 正文内容（紧凑布局）
        body_font_size = max(8, int(10 * font_scale))  # 最小8pt
        optimized_styles.add(ParagraphStyle(
            name='ModernBodyText',
            parent=optimized_styles['Normal'],
            fontName=self.chinese_font,
            fontSize=body_font_size,
            textColor=HexColor('#333333'),
            alignment=TA_LEFT,
            spaceBefore=max(2, int(3 * spacing_scale)),
            spaceAfter=max(2, int(3 * spacing_scale)),
            leading=max(10, int(body_font_size * 1.2)),
            leftIndent=0
        ))
        
        # 工作经历标题（紧凑布局）
        job_font_size = max(9, int(11 * font_scale))  # 最小9pt
        optimized_styles.add(ParagraphStyle(
            name='JobTitle',
            parent=optimized_styles['Normal'],
            fontName=self.chinese_medium_font,
            fontSize=job_font_size,
            textColor=HexColor('#2c3e50'),
            spaceBefore=max(4, int(6 * spacing_scale)),
            spaceAfter=max(1, int(2 * spacing_scale)),
            leading=max(11, int(job_font_size * 1.1))
        ))
        
        # 公司和时间（更紧凑）
        company_font_size = max(8, int(9 * font_scale))  # 最小8pt
        optimized_styles.add(ParagraphStyle(
            name='CompanyDate',
            parent=optimized_styles['Normal'],
            fontName=self.chinese_font,
            fontSize=company_font_size,
            textColor=HexColor('#7f8c8d'),
            spaceBefore=0,
            spaceAfter=max(2, int(3 * spacing_scale)),
            leading=max(10, int(company_font_size * 1.2))
        ))
        
        # 列表项（最紧凑）
        bullet_font_size = max(8, int(9 * font_scale))  # 最小8pt
        optimized_styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=optimized_styles['Normal'],
            fontName=self.chinese_font,
            fontSize=bullet_font_size,
            textColor=HexColor('#444444'),
            leftIndent=10,  # 减少缩进
            bulletIndent=0,
            spaceBefore=max(1, int(1.5 * spacing_scale)),
            spaceAfter=max(1, int(1.5 * spacing_scale)),
            leading=max(10, int(bullet_font_size * 1.2))
        ))
        
        # 技能项（紧凑布局）
        skill_font_size = max(8, int(9 * font_scale))  # 最小8pt
        optimized_styles.add(ParagraphStyle(
            name='SkillItem',
            parent=optimized_styles['Normal'],
            fontName=self.chinese_font,
            fontSize=skill_font_size,
            textColor=HexColor('#444444'),
            spaceBefore=max(1, int(1.5 * spacing_scale)),
            spaceAfter=max(1, int(1.5 * spacing_scale)),
            leading=max(10, int(skill_font_size * 1.2))
        ))
        
        return optimized_styles
    
    def generate_pdf(self, resume_data: Dict[str, Any], smart_onepage: bool = False) -> bytes:
        """生成现代化PDF简历"""
        buffer = io.BytesIO()
        
        # 智能一页模式处理
        current_styles = self.styles
        margins = self.default_margins.copy()
        
        if smart_onepage:
            print("启用智能一页模式")
            # 分析内容需求
            analysis = self._analyze_content_requirements(resume_data)
            print(f"内容分析: 预估高度 {analysis['estimated_height']:.1f}pt, 可用高度 {self.available_height:.1f}pt")
            
            if analysis['requires_compression']:
                compression_ratio = analysis['compression_ratio']
                print(f"需要压缩，压缩比例: {compression_ratio:.2f}")
                
                # 使用优化的样式
                current_styles = self._create_optimized_styles(compression_ratio)
                
                # 优化边距（适度减少）
                margin_reduction = max(0.8, compression_ratio + 0.15)
                margins = {
                    'top': int(self.default_margins['top'] * margin_reduction),
                    'bottom': int(self.default_margins['bottom'] * margin_reduction),
                    'left': int(self.default_margins['left'] * margin_reduction),
                    'right': int(self.default_margins['right'] * margin_reduction)
                }
                print(f"优化边距: 上下 {margins['top']}pt, 左右 {margins['left']}pt")
            else:
                print("内容适合一页，无需压缩")
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=margins['right'],
            leftMargin=margins['left'],
            topMargin=margins['top'],
            bottomMargin=margins['bottom']
        )
        
        # 构建文档内容
        story = []
        
        # 添加头部（姓名和联系信息）
        self._add_modern_header(story, resume_data, current_styles, smart_onepage)
        
        # 添加各个部分（使用新的布局）
        self._add_modern_sections(story, resume_data, current_styles, smart_onepage)
        
        # 构建PDF
        doc.build(story)
        
        # 获取PDF数据
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _add_modern_header(self, story, resume_data: Dict[str, Any], styles, smart_onepage: bool = False):
        """添加现代化头部信息"""
        personal_info = resume_data.get('personal_info', {})
        
        # 姓名 - 使用更大更现代的字体
        name = personal_info.get('name', '简历')
        # 清理姓名中的markdown符号
        name = self._clean_markdown(name)
        title_para = Paragraph(name, styles['NameTitle'])
        story.append(title_para)
        
        # 联系信息 - 简洁布局
        contact_items = []
        if personal_info.get('email'):
            email = self._clean_markdown(personal_info['email'])
            contact_items.append(email)
        if personal_info.get('phone'):
            phone = self._clean_markdown(personal_info['phone']).replace('\n-', '').strip()
            contact_items.append(phone)
        if personal_info.get('address'):
            address = self._clean_markdown(personal_info['address'])
            contact_items.append(address)
        
        if contact_items:
            contact_text = ' • '.join(contact_items)
            contact_para = Paragraph(contact_text, styles['ContactInfo'])
            story.append(contact_para)
        
        # 分隔线（智能一页模式下大幅减少间距）
        spacer_height = 3 if smart_onepage else 10
        story.append(Spacer(1, spacer_height))
    
    def _add_modern_sections(self, story, resume_data: Dict[str, Any], styles, smart_onepage: bool = False):
        """添加现代化的各个部分"""
        sections = resume_data.get('sections', [])
        # 动态计算文档宽度（考虑边距变化）
        margins = self.default_margins if not smart_onepage else {'left': 48, 'right': 48}
        doc_width = A4[0] - margins['left'] - margins['right']
        
        for section in sections:
            # 部分标题
            section_title = section.get('title', '')
            if section_title:
                # 清理markdown符号
                clean_title = self._clean_markdown(section_title)
                
                # 添加分隔线
                line_table = Table([['']], colWidths=[doc_width])
                line_table.setStyle(TableStyle([
                    ('LINEBELOW', (0, 0), (-1, -1), 1, HexColor('#3498db')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(line_table)
                
                # 智能一页模式下大幅减少间距
                spacer_height = 3 if smart_onepage else 8
                story.append(Spacer(1, spacer_height))
                
                # 章节标题
                title_para = Paragraph(clean_title.upper(), styles['SectionTitle'])
                story.append(title_para)
            
            # 部分内容
            section_type = section.get('type', 'other')
            items = section.get('items', [])
            
            if section_type == 'skills':
                self._add_modern_skills_section(story, items, styles)
            elif section_type in ['experience', 'education', 'projects']:
                self._add_modern_structured_section(story, items, section_type, styles)
            else:
                self._add_modern_generic_section(story, items, styles)
            
            # 章节间距（智能一页模式下大幅减少）
            section_spacer = 4 if smart_onepage else 12
            story.append(Spacer(1, section_spacer))
            
    def _add_modern_skills_section(self, story, items, styles):
        """添加现代化技能部分"""
        for item in items:
            content = item.get('content', '')
            if content:
                clean_content = self._clean_markdown(content)
                skill_para = Paragraph(f"• {clean_content}", styles['SkillItem'])
                story.append(skill_para)
    
    def _add_modern_structured_section(self, story, items, section_type, styles):
        """添加现代化结构化部分（经历、教育等）"""
        for item in items:
            content = item.get('content', '')
            if content:
                clean_content = self._clean_markdown(content)
                
                if item.get('type') == 'list_item':
                    # 列表项
                    list_para = Paragraph(f"• {clean_content}", styles['BulletPoint'])
                    story.append(list_para)
                else:
                    # 段落内容
                    # 检查是否是职位/标题行（包含 | 符号）
                    if '|' in clean_content and section_type in ['experience', 'education', 'projects']:
                        # 这是一个职位或教育标题行
                        job_para = Paragraph(clean_content, styles['JobTitle'])
                        story.append(job_para)
                    else:
                        # 普通段落
                        para = Paragraph(clean_content, styles['ModernBodyText'])
                        story.append(para)
    
    def _add_modern_generic_section(self, story, items, styles):
        """添加现代化通用部分"""
        for item in items:
            content = item.get('content', '')
            if content:
                clean_content = self._clean_markdown(content)
                
                if item.get('type') == 'list_item':
                    list_para = Paragraph(f"• {clean_content}", styles['BulletPoint'])
                    story.append(list_para)
                else:
                    para = Paragraph(clean_content, styles['ModernBodyText'])
                    story.append(para)
    
    def _add_skills_section(self, story, items):
        """添加技能部分"""
        for item in items:
            content = item.get('content', '')
            if content:
                # 技能项目使用项目符号
                skill_para = Paragraph(f"• {content}", self.styles['CustomListItem'])
                story.append(skill_para)
    
    def _add_structured_section(self, story, items):
        """添加结构化部分（经历、教育等）"""
        for item in items:
            content = item.get('content', '')
            if content:
                if item.get('type') == 'list_item':
                    # 列表项
                    list_para = Paragraph(f"• {content}", self.styles['CustomListItem'])
                    story.append(list_para)
                else:
                    # 段落
                    para = Paragraph(content, self.styles['CustomBody'])
                    story.append(para)
    
    def _add_generic_section(self, story, items):
        """添加通用部分"""
        for item in items:
            content = item.get('content', '')
            if content:
                if item.get('type') == 'list_item':
                    list_para = Paragraph(f"• {content}", self.styles['CustomListItem'])
                    story.append(list_para)
                else:
                    para = Paragraph(content, self.styles['CustomBody'])
                    story.append(para)
    
    def _clean_markdown(self, text: str) -> str:
        """清理Markdown标记，保留加粗、斜体等格式效果"""
        if not text:
            return ""
        
        # 移除标题标记 (#)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # 转换粗体标记 - 使用简单的font标签
        text = re.sub(r'\*\*(.*?)\*\*', rf'<font name="{self.chinese_bold_font}">\1</font>', text)
        
        # 转换斜体标记 - 使用中等字体，简单格式
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', rf'<font name="{self.chinese_medium_font}">\1</font>', text)
        
        # 转换下划线斜体标记
        text = re.sub(r'_([^_]+?)_', rf'<font name="{self.chinese_medium_font}">\1</font>', text)
        
        # 转换代码标记 - 使用背景色区分代码
        text = re.sub(r'`([^`]+?)`', rf'<font name="{self.chinese_font}" backColor="#f5f5f5">\1</font>', text)
        
        # 移除链接标记，保留文本
        text = re.sub(r'\[([^\]]+?)\]\([^)]*?\)', r'\1', text)
        
        # 移除列表标记但保留缩进
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # 移除数字列表标记
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 移除水平分隔线
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        
        # 移除块引用标记
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
        
        # 清理多余的空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # 清理行首标点符号问题 - 移除行首多余的标点符号
        text = re.sub(r'^[，。；：！？、]+', '', text, flags=re.MULTILINE)
        
        # 移除行首行尾空白
        text = text.strip()
        
        return text