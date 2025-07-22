import requests
import json
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DifyChatflowService:
    """浩流简历·flowork Dify 集成服务"""
    
    def __init__(self):
        # Dify API配置 - 使用正确的对话型应用API
        self.dify_api_base = os.getenv('DIFY_API_BASE', 'http://localhost/v1')
        self.dify_api_key = os.getenv('DIFY_API_KEY', '')
        
        # 会话管理
        self.active_sessions = {}  # conversation_id -> session_info
        
    def start_conversation(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        启动与浩流简历·flowork的对话
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            包含会话ID和初始消息的字典
        """
        try:
            # 生成本地会话ID用于跟踪
            local_session_id = str(uuid.uuid4())
            
            # 创建会话记录
            session_info = {
                'local_session_id': local_session_id,
                'dify_conversation_id': None,  # 将在首次API调用后获得
                'user_id': user_id,
                'created_at': datetime.utcnow(),
                'status': 'active',
                'messages': [],
                'context': {},
                'last_activity': datetime.utcnow()
            }
            
            self.active_sessions[local_session_id] = session_info
            
            # 不自动发送初始消息，等待用户主动开始对话
            return {
                'success': True,
                'conversation_id': local_session_id,
                'initial_message': '您好！我是浩流简历·flowork助手，我将引导您一步步创建个人简历。请告诉我您的基本信息，让我们开始吧！',
                'status': 'started'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'启动浩流简历·flowork对话失败: {str(e)}'
            }
    
    def send_message(self, conversation_id: str, message: str, inputs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送消息到浩流简历·flowork
        
        Args:
            conversation_id: 本地会话ID
            message: 用户消息
            inputs: 额外的输入参数
            
        Returns:
            浩流简历·flowork的响应结果
        """
        try:
            if conversation_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': '会话不存在或已过期'
                }
            
            session = self.active_sessions[conversation_id]
            session['last_activity'] = datetime.utcnow()
            
            # 发送消息到浩流简历·flowork
            response = self._send_message_to_workflow(
                conversation_id=conversation_id,
                message=message,
                inputs=inputs or {}
            )
            
            # 更新Dify对话ID（如果有变化）
            if response.get('conversation_id') and response.get('conversation_id') != session.get('dify_conversation_id'):
                session['dify_conversation_id'] = response.get('conversation_id')
            
            # 记录消息历史
            session['messages'].append({
                'type': 'user',
                'content': message,
                'timestamp': datetime.utcnow()
            })
            
            session['messages'].append({
                'type': 'assistant',
                'content': response.get('answer', ''),
                'timestamp': datetime.utcnow(),
                'metadata': response.get('metadata', {}),
                'message_id': response.get('message_id')
            })
            
            # 检查是否完成简历创建
            if self._is_resume_complete(response):
                session['status'] = 'completed'
                resume_content = self._extract_resume_content(response)
                return {
                    'success': True,
                    'message': response.get('answer', ''),
                    'conversation_id': conversation_id,
                    'status': 'completed',
                    'resume_content': resume_content
                }
            
            return {
                'success': True,
                'message': response.get('answer', ''),
                'conversation_id': conversation_id,
                'status': 'active',
                'suggestions': response.get('suggestions', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'发送消息失败: {str(e)}'
            }
    
    def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        """获取对话历史"""
        try:
            if conversation_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }
            
            session = self.active_sessions[conversation_id]
            return {
                'success': True,
                'conversation_id': conversation_id,
                'messages': session['messages'],
                'status': session['status'],
                'created_at': session['created_at'].isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取历史失败: {str(e)}'
            }
    
    def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """结束对话"""
        try:
            if conversation_id in self.active_sessions:
                self.active_sessions[conversation_id]['status'] = 'ended'
                # 可选：清理会话数据或移至历史记录
                del self.active_sessions[conversation_id]
            
            return {
                'success': True,
                'message': '对话已结束'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'结束对话失败: {str(e)}'
            }
    
    def _send_message_to_workflow(self, conversation_id: str, message: str, inputs: Dict) -> Dict[str, Any]:
        """
        发送消息到浩流简历·flowork Dify 对话应用
        
        Args:
            conversation_id: 会话ID
            message: 消息内容
            inputs: 输入参数
            
        Returns:
            Dify API响应
        """
        try:
            # 使用正确的Dify对话型应用API端点
            url = f"{self.dify_api_base}/chat-messages"
            
            headers = {
                'Authorization': f'Bearer {self.dify_api_key}',
                'Content-Type': 'application/json'
            }
            
            # 获取实际的Dify对话ID
            session = self.active_sessions.get(conversation_id, {})
            dify_conversation_id = session.get('dify_conversation_id', '')
            
            # 构建符合Dify chat-messages API的请求格式
            payload = {
                'inputs': inputs,  # 应用定义的输入变量
                'query': message,  # 用户输入/提问内容
                'response_mode': 'streaming',  # 流式模式，支持实时响应
                'user': f'user-{conversation_id}',  # 用户标识，使用本地会话ID区分
                'conversation_id': dify_conversation_id,  # Dify对话ID，首次为空
                'auto_generate_name': True  # 自动生成对话标题
            }
            
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=90)
            response.raise_for_status()
            
            # 处理流式响应
            return self._handle_streaming_response(response, conversation_id)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"调用浩流简历·flowork失败: {str(e)}")
    
    def _is_resume_complete(self, response: Dict) -> bool:
        """检查浩流简历·flowork是否创建完成"""
        # 检查响应中是否包含完成标识
        answer = response.get('answer', '').lower()
        metadata = response.get('metadata', {})
        
        # 检查完成标识关键词
        completion_keywords = [
            '简历创建完成', '简历已生成', '简历制作完成', '简历生成完毕',
            'resume complete', 'resume generated', '创建完毕', '已完成',
            '浩流简历', '简历内容如下', '您的简历已经准备好了'
        ]
        
        for keyword in completion_keywords:
            if keyword.lower() in answer:
                return True
        
        # 检查是否包含markdown格式的简历内容
        if ('# ' in response.get('answer', '') and 
            ('## 个人信息' in response.get('answer', '') or 
             '## 工作经历' in response.get('answer', '') or
             '## 教育背景' in response.get('answer', ''))):
            return True
        
        # 检查metadata中的完成标识
        if metadata.get('status') == 'completed' or metadata.get('resume_ready'):
            return True
        
        return False
    
    def _extract_resume_content(self, response: Dict) -> Optional[Dict]:
        """从浩流简历·flowork响应中提取简历内容"""
        try:
            # 方式1: 直接从answer中提取简历markdown
            answer = response.get('answer', '')
            if answer and ('# ' in answer or '## ' in answer):  # 包含markdown标题
                # 提取姓名作为简历标题
                title = '浩流简历·flowork生成的简历'
                lines = answer.split('\n')
                for line in lines:
                    if line.startswith('# ') and line.strip() != '# ':
                        title = line.replace('# ', '').strip() + ' - 浩流简历·flowork'
                        break
                
                return {
                    'markdown': answer,
                    'title': title
                }
            
            # 方式2: 从metadata中提取
            metadata = response.get('metadata', {})
            if 'resume_content' in metadata:
                return {
                    'markdown': metadata['resume_content'],
                    'title': metadata.get('resume_title', '浩流简历·flowork生成的简历')
                }
            
            # 方式3: 检查retriever_resources（如果Dify返回结构化数据）
            if metadata.get('retriever_resources'):
                resources = metadata.get('retriever_resources', [])
                for resource in resources:
                    if 'resume' in resource.get('content', '').lower():
                        return {
                            'markdown': resource.get('content', ''),
                            'title': '浩流简历·flowork生成的简历'
                        }
            
            # 如果answer包含简历相关信息但不是标准markdown，尝试包装
            if answer and any(keyword in answer.lower() for keyword in ['姓名', '电话', '邮箱', '工作经历', '教育背景']):
                return {
                    'markdown': f"# 个人简历\n\n{answer}",
                    'title': '浩流简历·flowork生成的简历'
                }
            
            return None
            
        except Exception as e:
            print(f"提取浩流简历内容失败: {str(e)}")
            return None
    
    def cleanup_expired_sessions(self, max_age_minutes: int = 30):
        """清理过期的会话"""
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for conv_id, session in self.active_sessions.items():
                last_activity = session.get('last_activity', session.get('created_at'))
                age_minutes = (current_time - last_activity).total_seconds() / 60
                
                if age_minutes > max_age_minutes:
                    expired_sessions.append(conv_id)
            
            for conv_id in expired_sessions:
                del self.active_sessions[conv_id]
            
            print(f"清理了 {len(expired_sessions)} 个过期会话")
            
        except Exception as e:
            print(f"清理会话时出错: {str(e)}")
    
    def _handle_streaming_response(self, response, conversation_id):
        """处理Dify流式响应"""
        try:
            full_answer = ""
            dify_conversation_id = None
            message_id = None
            metadata = {}
            
            # 解析流式数据
            for line in response.iter_lines(decode_unicode=True):
                if not line.strip():
                    continue
                    
                # 处理SSE格式: data: {...}
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # 移除 'data: ' 前缀
                        
                        event = data.get('event', '')
                        
                        if event == 'message':
                            # 消息块事件
                            full_answer += data.get('answer', '')
                            if not dify_conversation_id:
                                dify_conversation_id = data.get('conversation_id')
                            if not message_id:
                                message_id = data.get('message_id')
                        
                        elif event == 'message_end':
                            # 消息结束事件，包含完整的metadata
                            metadata = data.get('metadata', {})
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            return {
                'answer': full_answer,
                'conversation_id': dify_conversation_id or conversation_id,
                'message_id': message_id,
                'metadata': metadata,
                'suggestions': []
            }
            
        except Exception as e:
            raise Exception(f"处理流式响应失败: {str(e)}")