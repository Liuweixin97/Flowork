from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Resume, User
from services.markdown_parser import ResumeMarkdownParser
from services.pdf_generator import ResumePDFGenerator
from services.html_pdf_generator import HTMLPDFGenerator
from services.auth_service import AuthService, is_token_blacklisted
import io
import os
from datetime import datetime

resume_bp = Blueprint('resume', __name__)
parser = ResumeMarkdownParser()
pdf_generator = ResumePDFGenerator()
html_pdf_generator = HTMLPDFGenerator()

def get_current_user_or_none():
    """获取当前用户，无token时返回None"""
    try:
        user_id = get_jwt_identity()
        if user_id:
            return User.find_by_public_id(user_id)
    except:
        pass
    return None

def check_token_blacklist():
    """检查token是否在黑名单中"""
    try:
        jti = get_jwt()['jti']
        if is_token_blacklisted(jti):
            return jsonify({
                'success': False,
                'errors': ['令牌已失效，请重新登录']
            }), 401
    except:
        pass
    return None

@resume_bp.route('/api/resumes', methods=['POST'])
@jwt_required()
def create_resume():
    """创建新简历"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        current_user = AuthService.get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'errors': ['用户未找到']
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'errors': ['请提供简历数据']
            }), 400
        
        # 获取简历内容
        title = data.get('title', '我的简历')
        raw_markdown = data.get('raw_markdown', '# 我的简历\n\n请在这里编辑您的简历内容...')
        is_public = data.get('is_public', False)
        
        # 解析Markdown为结构化数据
        structured_data = parser.parse(raw_markdown)
        
        # 创建简历记录
        resume = Resume(
            title=title,
            raw_markdown=raw_markdown,
            is_public=is_public,
            user_id=current_user.id
        )
        resume.set_structured_data(structured_data)
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '简历创建成功',
            'resume': resume.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '创建简历失败'
        }), 500

def get_or_create_dify_user():
    """获取或创建Dify系统用户"""
    try:
        # 尝试找到现有的Dify系统用户
        dify_user = User.query.filter_by(username='dify_system').first()
        
        if not dify_user:
            print("[DIFY] 创建Dify系统用户")
            # 创建Dify系统用户
            dify_user = User(
                username='dify_system',
                email='dify@system.local',
                password='dify_system_password_123',
                full_name='Dify系统用户'
            )
            dify_user.is_admin = False
            db.session.add(dify_user)
            db.session.commit()
            print(f"[DIFY] Dify系统用户已创建: ID={dify_user.id}")
        else:
            print(f"[DIFY] 找到现有Dify系统用户: ID={dify_user.id}")
        
        return dify_user
    except Exception as e:
        print(f"[DIFY] 创建Dify系统用户失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 回滚
        db.session.rollback()
        
        # 重新尝试查找现有用户
        existing_user = User.query.filter_by(username='dify_system').first()
        if existing_user:
            print(f"[DIFY] 找到回滚后的现有用户: ID={existing_user.id}")
            return existing_user
        
        # 如果还是没有，尝试使用第一个用户或admin用户作为fallback
        fallback_user = User.query.filter_by(username='admin').first() or User.query.first()
        if fallback_user:
            print(f"[DIFY] 使用fallback用户: {fallback_user.username} (ID={fallback_user.id})")
            return fallback_user
            
        print("[DIFY] 严重错误：无法找到任何用户，无法处理简历")
        return None

@resume_bp.route('/api/resumes/from-dify', methods=['POST'])
@jwt_required(optional=True)
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
        user_id = data.get('user_id', None)  # 可选用户ID
        
        if not markdown_content:
            return jsonify({'error': '缺少简历内容'}), 400
        
        # 解析Markdown为结构化数据
        structured_data = parser.parse(markdown_content)
        
        # 获取用户信息，优先使用当前认证用户
        user = get_current_user_or_none()
        
        # 如果没有当前认证用户，尝试使用传递的user_id
        if not user and user_id:
            user = User.find_by_public_id(user_id) or User.query.get(user_id)
        
        # 如果依然没有用户，使用Dify系统用户
        if not user:
            user = get_or_create_dify_user()
            if not user:
                return jsonify({
                    'error': '系统错误：无法找到或创建用户，请联系管理员',
                    'details': '数据库中没有任何用户记录'
                }), 500
            print(f"[DIFY] 使用Dify系统用户: {user.username} (ID: {user.id})")
        else:
            print(f"[DIFY] 找到认证用户: {user.username} (ID: {user.id})")
        
        # 创建简历记录
        resume = Resume(
            title=title,
            raw_markdown=markdown_content,
            user_id=user.id,  # 现在总是有用户
            is_public=True  # Dify生成的简历默认设为公开
        )
        resume.set_structured_data(structured_data)
        
        db.session.add(resume)
        db.session.commit()
        
        # 构建前端编辑页面URL  
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        edit_url = f"/edit/{resume.id}"
        full_redirect_url = f"{frontend_url}{edit_url}"
        
        # 🎯 创建简历通知状态，前端会检查这个状态并显示弹窗
        try:
            import json
            from pathlib import Path
            
            # 创建通知状态文件
            notification_data = {
                'type': 'resume_created',
                'resume_id': resume.id,
                'title': resume.title,
                'edit_url': edit_url,
                'redirect_url': full_redirect_url,
                'timestamp': datetime.utcnow().isoformat(),
                'shown': False  # 标记是否已显示给用户
            }
            
            # 保存到临时文件
            notification_file = Path('instance/latest_resume_notification.json')
            notification_file.parent.mkdir(exist_ok=True)
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, ensure_ascii=False, indent=2)
            
            print(f"[NOTIFICATION] 简历创建通知已保存: {resume.title} -> {full_redirect_url}")
            
        except Exception as e:
            print(f"[NOTIFICATION] 保存通知状态失败: {e}")
        
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
@jwt_required(optional=True)
def get_resumes():
    """获取简历列表（支持认证和非认证访问）"""
    try:
        current_user = get_current_user_or_none()
        
        # 只有在有认证用户的情况下才检查token黑名单
        if current_user:
            blacklist_result = check_token_blacklist()
            if blacklist_result:
                return blacklist_result
        
        if current_user:
            # 认证用户：显示自己的简历 + 公开简历
            if current_user.is_admin:
                # 管理员：显示所有简历
                resumes = Resume.query.order_by(Resume.updated_at.desc()).all()
            else:
                # 普通用户：显示自己的简历和公开简历
                resumes = Resume.query.filter(
                    db.or_(
                        Resume.user_id == current_user.id,
                        Resume.is_public == True
                    )
                ).order_by(Resume.updated_at.desc()).all()
        else:
            # 未认证用户：只显示公开简历
            resumes = Resume.query.filter_by(is_public=True).order_by(Resume.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'resumes': [resume.to_dict(include_content=False) for resume in resumes],
            'total': len(resumes),
            'current_user': current_user.to_dict() if current_user else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '获取简历列表失败'
        }), 500

@resume_bp.route('/api/resumes/<int:resume_id>', methods=['GET'])
@jwt_required(optional=True)
def get_resume(resume_id):
    """获取特定简历"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        resume = Resume.query.get_or_404(resume_id)
        current_user = get_current_user_or_none()
        
        # 检查访问权限
        if not resume.can_access(current_user):
            return jsonify({
                'success': False,
                'errors': ['没有权限访问此简历']
            }), 403
        
        return jsonify({
            'success': True,
            'resume': resume.to_dict(),
            'can_edit': resume.can_edit(current_user)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '获取简历失败'
        }), 500

@resume_bp.route('/api/resumes/<int:resume_id>', methods=['PUT'])
@jwt_required()
def update_resume(resume_id):
    """更新简历"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        resume = Resume.query.get_or_404(resume_id)
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({
                'success': False,
                'errors': ['用户未找到']
            }), 401
        
        # 检查编辑权限
        if not resume.can_edit(current_user):
            return jsonify({
                'success': False,
                'errors': ['没有权限编辑此简历']
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'errors': ['请提供更新数据']
            }), 400
        
        # 更新简历字段
        if 'title' in data:
            resume.title = data['title']
        
        if 'is_public' in data and isinstance(data['is_public'], bool):
            resume.is_public = data['is_public']
        
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
        return jsonify({
            'success': False,
            'error': '更新简历失败'
        }), 500

@resume_bp.route('/api/resumes/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """删除简历"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        resume = Resume.query.get_or_404(resume_id)
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({
                'success': False,
                'errors': ['用户未找到']
            }), 401
        
        # 检查删除权限
        if not resume.can_edit(current_user):
            return jsonify({
                'success': False,
                'errors': ['没有权限删除此简历']
            }), 403
        
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '简历删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '删除简历失败'
        }), 500

@resume_bp.route('/api/resumes/<int:resume_id>/pdf', methods=['GET'])
@jwt_required(optional=True)
def export_pdf(resume_id):
    """导出简历为PDF"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        resume = Resume.query.get_or_404(resume_id)
        current_user = get_current_user_or_none()
        
        # 检查访问权限
        if not resume.can_access(current_user):
            return jsonify({
                'success': False,
                'errors': ['没有权限访问此简历']
            }), 403
        
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

@resume_bp.route('/api/resumes/<int:resume_id>/pdf-html', methods=['GET'])
@jwt_required(optional=True)
def export_pdf_html(resume_id):
    """使用HTML渲染方式导出简历为PDF"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        resume = Resume.query.get_or_404(resume_id)
        current_user = get_current_user_or_none()
        
        # 检查访问权限
        if not resume.can_access(current_user):
            return jsonify({
                'success': False,
                'errors': ['没有权限访问此简历']
            }), 403
        
        structured_data = resume.get_structured_data()
        
        if not structured_data:
            # 如果没有结构化数据，重新解析
            structured_data = parser.parse(resume.raw_markdown)
            resume.set_structured_data(structured_data)
            db.session.commit()
        
        # 检查智能一页参数
        smart_onepage = request.args.get('smart_onepage', 'false').lower() == 'true'
        
        # 生成PDF（使用HTML渲染方式）
        pdf_bytes = html_pdf_generator.generate_pdf(structured_data, smart_onepage=smart_onepage)
        
        # 创建文件流
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        # 文件名添加HTML标识
        method_suffix = "_HTML渲染" 
        onepage_suffix = "_智能一页" if smart_onepage else ""
        filename = f"{resume.title.replace(' ', '_')}{method_suffix}{onepage_suffix}.pdf"
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'HTML转PDF生成失败: {str(e)}'}), 500

@resume_bp.route('/api/resumes/<int:resume_id>/html', methods=['GET'])
@jwt_required(optional=True)
def get_resume_html(resume_id):
    """获取简历的HTML内容（用于预览或调试）"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        resume = Resume.query.get_or_404(resume_id)
        current_user = get_current_user_or_none()
        
        # 检查访问权限
        if not resume.can_access(current_user):
            return jsonify({
                'success': False,
                'errors': ['没有权限访问此简历']
            }), 403
        
        structured_data = resume.get_structured_data()
        
        if not structured_data:
            # 如果没有结构化数据，重新解析
            structured_data = parser.parse(resume.raw_markdown)
            resume.set_structured_data(structured_data)
            db.session.commit()
        
        # 检查智能一页参数
        smart_onepage = request.args.get('smart_onepage', 'false').lower() == 'true'
        
        # 获取HTML内容
        html_content = html_pdf_generator.get_html_content(structured_data, smart_onepage=smart_onepage)
        
        # 检查是否返回原始HTML（用于浏览器预览）
        raw = request.args.get('raw', 'false').lower() == 'true'
        if raw:
            from flask import Response
            return Response(html_content, mimetype='text/html')
        
        return jsonify({
            'success': True,
            'html_content': html_content,
            'smart_onepage': smart_onepage
        })
        
    except Exception as e:
        return jsonify({'error': f'HTML生成失败: {str(e)}'}), 500

@resume_bp.route('/api/resumes/<int:resume_id>/preview', methods=['GET'])
@jwt_required(optional=True)
def preview_html(resume_id):
    """预览简历HTML"""
    try:
        # 检查token黑名单
        blacklist_result = check_token_blacklist()
        if blacklist_result:
            return blacklist_result
        
        resume = Resume.query.get_or_404(resume_id)
        current_user = get_current_user_or_none()
        
        # 检查访问权限
        if not resume.can_access(current_user):
            return jsonify({
                'success': False,
                'errors': ['没有权限访问此简历']
            }), 403
        
        html_content = parser.markdown_to_html(resume.raw_markdown)
        
        return jsonify({
            'success': True,
            'html_content': html_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/api/resume-notification', methods=['GET'])
def get_resume_notification():
    """获取最新的简历创建通知"""
    try:
        import json
        from pathlib import Path
        
        notification_file = Path('instance/latest_resume_notification.json')
        
        if not notification_file.exists():
            return jsonify({
                'success': True,
                'notification': None
            })
        
        # 读取通知数据
        with open(notification_file, 'r', encoding='utf-8') as f:
            notification_data = json.load(f)
        
        # 检查是否已经显示过
        if notification_data.get('shown', True):
            return jsonify({
                'success': True,
                'notification': None
            })
        
        return jsonify({
            'success': True,
            'notification': notification_data
        })
        
    except Exception as e:
        print(f"[API] 获取通知失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@resume_bp.route('/api/resume-notification', methods=['POST'])
def mark_notification_shown():
    """标记通知已显示"""
    try:
        import json
        from pathlib import Path
        
        notification_file = Path('instance/latest_resume_notification.json')
        
        if notification_file.exists():
            # 读取现有数据
            with open(notification_file, 'r', encoding='utf-8') as f:
                notification_data = json.load(f)
            
            # 标记为已显示
            notification_data['shown'] = True
            
            # 写回文件
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': '通知已标记为已显示'
        })
        
    except Exception as e:
        print(f"[API] 标记通知失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@resume_bp.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'resume-editor',
        'version': '1.3.0',
        'timestamp': datetime.utcnow().isoformat()
    })