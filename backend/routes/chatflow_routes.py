from flask import Blueprint, request, jsonify, Response
from services.dify_chatflow_service import DifyChatflowService
from services.markdown_parser import ResumeMarkdownParser
from models import db, Resume
from datetime import datetime
import logging
import json

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chatflow_bp = Blueprint('chatflow', __name__)
dify_service = DifyChatflowService()
parser = ResumeMarkdownParser()

@chatflow_bp.route('/api/chatflow/start', methods=['POST'])
def start_chatflow():
    """启动Dify Chatflow对话"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        logger.info(f"启动Chatflow对话，用户ID: {user_id}")
        
        result = dify_service.start_conversation(user_id)
        
        if result['success']:
            logger.info(f"对话启动成功，会话ID: {result['conversation_id']}")
            return jsonify(result), 200
        else:
            logger.error(f"对话启动失败: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"启动对话时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'启动对话失败: {str(e)}'
        }), 500

@chatflow_bp.route('/api/chatflow/message', methods=['POST'])
def send_message():
    """发送消息到Chatflow"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求数据'
            }), 400
        
        conversation_id = data.get('conversation_id')
        message = data.get('message')
        inputs = data.get('inputs', {})
        
        if not conversation_id or not message:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: conversation_id 和 message'
            }), 400
        
        logger.info(f"发送消息到会话 {conversation_id}: {message[:100]}...")
        
        result = dify_service.send_message(conversation_id, message, inputs)
        
        if result['success']:
            # 如果对话完成且包含简历内容，自动创建简历记录
            if result.get('status') == 'completed' and result.get('resume_content'):
                try:
                    resume_data = result['resume_content']
                    resume = create_resume_from_chatflow(
                        markdown_content=resume_data['markdown'],
                        title=resume_data['title'],
                        conversation_id=conversation_id
                    )
                    
                    result['resume_id'] = resume.id
                    result['edit_url'] = f'/edit/{resume.id}'
                    
                    logger.info(f"自动创建简历成功，ID: {resume.id}")
                    
                except Exception as resume_error:
                    logger.error(f"创建简历失败: {str(resume_error)}")
                    # 不影响对话流程，继续返回结果
            
            return jsonify(result), 200
        else:
            logger.error(f"发送消息失败: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"发送消息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'发送消息失败: {str(e)}'
        }), 500

@chatflow_bp.route('/api/chatflow/history/<conversation_id>', methods=['GET'])
def get_conversation_history(conversation_id):
    """获取对话历史"""
    try:
        logger.info(f"获取对话历史，会话ID: {conversation_id}")
        
        result = dify_service.get_conversation_history(conversation_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"获取对话历史时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取对话历史失败: {str(e)}'
        }), 500

@chatflow_bp.route('/api/chatflow/end', methods=['POST'])
def end_chatflow():
    """结束Chatflow对话"""
    try:
        data = request.get_json()
        
        if not data or 'conversation_id' not in data:
            return jsonify({
                'success': False,
                'error': '缺少conversation_id参数'
            }), 400
        
        conversation_id = data['conversation_id']
        logger.info(f"结束对话，会话ID: {conversation_id}")
        
        result = dify_service.end_conversation(conversation_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"结束对话时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'结束对话失败: {str(e)}'
        }), 500

@chatflow_bp.route('/api/chatflow/create-resume', methods=['POST'])
def create_resume_from_chatflow_manual():
    """手动从Chatflow结果创建简历"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求数据'
            }), 400
        
        markdown_content = data.get('markdown_content')
        title = data.get('title', 'AI生成的简历')
        conversation_id = data.get('conversation_id')
        
        if not markdown_content:
            return jsonify({
                'success': False,
                'error': '缺少简历内容'
            }), 400
        
        resume = create_resume_from_chatflow(markdown_content, title, conversation_id)
        
        logger.info(f"手动创建简历成功，ID: {resume.id}")
        
        return jsonify({
            'success': True,
            'message': '简历创建成功',
            'resume_id': resume.id,
            'edit_url': f'/edit/{resume.id}',
            'resume': resume.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"创建简历时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'创建简历失败: {str(e)}'
        }), 500

def create_resume_from_chatflow(markdown_content, title, conversation_id=None):
    """从Chatflow结果创建简历记录"""
    try:
        # 解析Markdown为结构化数据
        structured_data = parser.parse(markdown_content)
        
        # 创建简历记录
        resume = Resume(
            title=title,
            raw_markdown=markdown_content
        )
        resume.set_structured_data(structured_data)
        
        # 如果有会话ID，可以添加到metadata中
        if conversation_id:
            current_data = resume.get_structured_data() or {}
            current_data['_metadata'] = {
                'source': 'dify_chatflow',
                'conversation_id': conversation_id,
                'created_at': datetime.utcnow().isoformat()
            }
            resume.set_structured_data(current_data)
        
        db.session.add(resume)
        db.session.commit()
        
        return resume
        
    except Exception as e:
        db.session.rollback()
        raise Exception(f'数据库操作失败: {str(e)}')

@chatflow_bp.route('/api/chatflow/status', methods=['GET'])
def chatflow_status():
    """获取Chatflow服务状态"""
    try:
        # 检查服务状态
        active_sessions_count = len(dify_service.active_sessions)
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'dify-chatflow',
            'active_sessions': active_sessions_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'状态检查失败: {str(e)}'
        }), 500

# 定期清理过期会话的后台任务
@chatflow_bp.route('/api/chatflow/cleanup', methods=['POST'])
def cleanup_sessions():
    """清理过期会话（管理员接口）"""
    try:
        data = request.get_json() or {}
        max_age_minutes = data.get('max_age_minutes', 30)
        
        # 执行清理
        before_count = len(dify_service.active_sessions)
        dify_service.cleanup_expired_sessions(max_age_minutes)
        after_count = len(dify_service.active_sessions)
        
        cleaned_count = before_count - after_count
        
        logger.info(f"会话清理完成，清理了 {cleaned_count} 个过期会话")
        
        return jsonify({
            'success': True,
            'message': f'清理了 {cleaned_count} 个过期会话',
            'before_count': before_count,
            'after_count': after_count
        }), 200
        
    except Exception as e:
        logger.error(f"清理会话时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'清理失败: {str(e)}'
        }), 500

@chatflow_bp.route('/api/chatflow/stream', methods=['POST'])
def stream_message():
    """流式发送消息到浩流简历·flowork"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求数据'
            }), 400
        
        conversation_id = data.get('conversation_id')
        message = data.get('message')
        inputs = data.get('inputs', {})
        
        if not conversation_id or not message:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: conversation_id 和 message'
            }), 400
        
        logger.info(f"流式发送消息到会话 {conversation_id}: {message[:100]}...")
        
        def generate():
            try:
                # 获取会话信息
                if conversation_id not in dify_service.active_sessions:
                    yield f"data: {json.dumps({'success': False, 'error': '会话不存在或已过期'})}\n\n"
                    return
                    
                session = dify_service.active_sessions[conversation_id]
                session['last_activity'] = datetime.utcnow()
                
                # 直接调用Dify API进行流式请求
                url = f"{dify_service.dify_api_base}/chat-messages"
                headers = {
                    'Authorization': f'Bearer {dify_service.dify_api_key}',
                    'Content-Type': 'application/json'
                }
                
                dify_conversation_id = session.get('dify_conversation_id', '')
                payload = {
                    'inputs': inputs,
                    'query': message,
                    'response_mode': 'streaming',
                    'user': f'user-{conversation_id}',
                    'conversation_id': dify_conversation_id,
                    'auto_generate_name': True
                }
                
                import requests
                response = requests.post(url, headers=headers, json=payload, stream=True, timeout=90)
                response.raise_for_status()
                
                # 记录用户消息
                session['messages'].append({
                    'type': 'user',
                    'content': message,
                    'timestamp': datetime.utcnow()
                })
                
                full_answer = ""
                message_id = None
                
                # 转发流式响应
                for line in response.iter_lines(decode_unicode=True):
                    if not line.strip():
                        continue
                    
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            event = data.get('event', '')
                            
                            if event == 'message':
                                # 消息块事件
                                chunk = data.get('answer', '')
                                full_answer += chunk
                                if not message_id:
                                    message_id = data.get('message_id')
                                
                                # 转发给前端
                                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'success': True})}\n\n"
                                
                            elif event == 'message_end':
                                # 消息结束
                                metadata = data.get('metadata', {})
                                
                                # 记录AI回复
                                session['messages'].append({
                                    'type': 'assistant',
                                    'content': full_answer,
                                    'timestamp': datetime.utcnow(),
                                    'metadata': metadata,
                                    'message_id': message_id
                                })
                                
                                # 检查是否完成简历创建
                                is_complete = dify_service._is_resume_complete({'answer': full_answer, 'metadata': metadata})
                                resume_content = None
                                if is_complete:
                                    session['status'] = 'completed'
                                    resume_content = dify_service._extract_resume_content({'answer': full_answer, 'metadata': metadata})
                                
                                yield f"data: {json.dumps({'type': 'end', 'success': True, 'status': 'completed' if is_complete else 'active', 'resume_content': resume_content})}\n\n"
                                break
                                
                        except json.JSONDecodeError:
                            continue
                    
            except Exception as e:
                logger.error(f"流式处理错误: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'success': False, 'error': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream', headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
        
    except Exception as e:
        logger.error(f"流式发送消息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'流式发送消息失败: {str(e)}'
        }), 500