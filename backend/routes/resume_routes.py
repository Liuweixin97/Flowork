from flask import Blueprint, request, jsonify, send_file
from models import db, Resume
from services.markdown_parser import ResumeMarkdownParser
from services.pdf_generator import ResumePDFGenerator
import io
import os
from datetime import datetime

resume_bp = Blueprint('resume', __name__)
parser = ResumeMarkdownParser()
pdf_generator = ResumePDFGenerator()

@resume_bp.route('/api/resumes/from-dify', methods=['POST'])
def receive_from_dify():
    """接收来自Dify的HTTP请求节点的简历数据"""
    try:
        # 详细的请求日志
        print(f"[DIFY] 收到请求 - Method: {request.method}")
        print(f"[DIFY] Content-Type: {request.content_type}")
        print(f"[DIFY] Headers: {dict(request.headers)}")
        
        # 获取原始数据
        raw_data = request.get_data(as_text=True)
        print(f"[DIFY] 原始数据长度: {len(raw_data)}")
        print(f"[DIFY] 原始数据预览: {raw_data[:200]}...")
        
        # 尝试解析JSON
        try:
            data = request.get_json(force=True)
            print(f"[DIFY] JSON解析成功，数据类型: {type(data)}")
            print(f"[DIFY] JSON数据键: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        except Exception as json_error:
            print(f"[DIFY] JSON解析失败: {json_error}")
            return jsonify({
                'error': f'JSON解析失败: {str(json_error)}',
                'raw_data_preview': raw_data[:100],
                'content_type': request.content_type
            }), 400
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 从Dify传来的数据中提取Markdown内容
        markdown_content = data.get('resume_markdown', data.get('content', data.get('markdown', '')))
        title = data.get('title', '来自Dify的简历')
        
        if not markdown_content:
            return jsonify({'error': '缺少简历内容'}), 400
        
        # 解析Markdown为结构化数据
        structured_data = parser.parse(markdown_content)
        
        # 创建简历记录
        resume = Resume(
            title=title,
            raw_markdown=markdown_content
        )
        resume.set_structured_data(structured_data)
        
        db.session.add(resume)
        db.session.commit()
        
        # 构建前端编辑页面URL  
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3002')
        edit_url = f"/edit/{resume.id}"
        full_redirect_url = f"{frontend_url}{edit_url}"
        
        # 🎯 简历创建成功，前端轮询机制会自动检测到新简历并跳转
        print(f"[AUTO_REDIRECT] 简历已创建，等待前端自动跳转: {resume.title} -> {full_redirect_url}")
        
        # 检查是否需要HTTP重定向（兼容旧方式）
        auto_redirect = request.args.get('auto_redirect', '').lower() == 'true'
        if not auto_redirect and isinstance(data, dict):
            auto_redirect = data.get('auto_redirect', False)
        
        if auto_redirect:
            # HTTP重定向：返回302重定向  
            from flask import redirect
            return redirect(full_redirect_url, code=302)
        else:
            # 标准API响应：返回JSON，前端轮询会检测到这个新简历
            return jsonify({
                'success': True,
                'message': '简历接收成功，前端将自动跳转',
                'resume_id': resume.id,
                'edit_url': edit_url,
                'redirect_url': full_redirect_url,
                'auto_redirect_enabled': True
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'处理请求时发生错误: {str(e)}'}), 500

@resume_bp.route('/api/resumes', methods=['GET'])
def get_resumes():
    """获取所有简历列表"""
    try:
        resumes = Resume.query.order_by(Resume.updated_at.desc()).all()
        return jsonify({
            'success': True,
            'resumes': [resume.to_dict() for resume in resumes]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/api/resumes/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    """获取特定简历"""
    try:
        resume = Resume.query.get_or_404(resume_id)
        return jsonify({
            'success': True,
            'resume': resume.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/api/resumes/<int:resume_id>', methods=['PUT'])
def update_resume(resume_id):
    """更新简历"""
    try:
        resume = Resume.query.get_or_404(resume_id)
        data = request.get_json()
        
        if 'title' in data:
            resume.title = data['title']
        
        if 'raw_markdown' in data:
            resume.raw_markdown = data['raw_markdown']
            # 重新解析Markdown
            structured_data = parser.parse(data['raw_markdown'])
            resume.set_structured_data(structured_data)
        
        if 'structured_data' in data:
            resume.set_structured_data(data['structured_data'])
        
        resume.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '简历更新成功',
            'resume': resume.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/api/resumes/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    """删除简历"""
    try:
        resume = Resume.query.get_or_404(resume_id)
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '简历删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/api/resumes/<int:resume_id>/pdf', methods=['GET'])
def export_pdf(resume_id):
    """导出简历为PDF"""
    try:
        resume = Resume.query.get_or_404(resume_id)
        structured_data = resume.get_structured_data()
        
        if not structured_data:
            # 如果没有结构化数据，重新解析
            structured_data = parser.parse(resume.raw_markdown)
            resume.set_structured_data(structured_data)
            db.session.commit()
        
        # 检查智能一页参数
        smart_onepage = request.args.get('smart_onepage', 'false').lower() == 'true'
        
        # 生成PDF（支持智能一页模式）
        pdf_bytes = pdf_generator.generate_pdf(structured_data, smart_onepage=smart_onepage)
        
        # 创建文件流
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        # 文件名添加智能一页标识
        filename_suffix = "_智能一页" if smart_onepage else ""
        filename = f"{resume.title.replace(' ', '_')}{filename_suffix}.pdf"
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'PDF生成失败: {str(e)}'}), 500

@resume_bp.route('/api/resumes/<int:resume_id>/preview', methods=['GET'])
def preview_html(resume_id):
    """预览简历HTML"""
    try:
        resume = Resume.query.get_or_404(resume_id)
        html_content = parser.markdown_to_html(resume.raw_markdown)
        
        return jsonify({
            'success': True,
            'html_content': html_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'resume-editor',
        'timestamp': datetime.utcnow().isoformat()
    })