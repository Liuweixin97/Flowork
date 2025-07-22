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
    """Dify Chatflow 集成服务"""
    
    def __init__(self):
        # Dify API配置
        self.dify_api_base = os.getenv('DIFY_API_BASE', 'http://localhost:8001/v1')
        self.dify_api_key = os.getenv('DIFY_API_KEY', '')
        self.app_id = os.getenv('DIFY_APP_ID', '')
        self.workflow_id = os.getenv('DIFY_WORKFLOW_ID', '')  # 浩流简历·flowork 工作流ID
        
        # 会话管理
        self.active_sessions = {}  # conversation_id -> session_info
        
    def start_conversation(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        启动与Dify Chatflow的对话
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            包含会话ID和初始消息的字典
        """
        try:
            conversation_id = str(uuid.uuid4())
            
            # 创建会话记录
            session_info = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'created_at': datetime.utcnow(),
                'status': 'active',
                'messages': [],
                'context': {},
                'last_activity': datetime.utcnow()
            }
            
            self.active_sessions[conversation_id] = session_info
            
            # 发送初始消息启动工作流
            initial_response = self._send_message_to_workflow(
                conversation_id=conversation_id,
                message="开始创建简历",
                inputs={}
            )
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'initial_message': initial_response.get('answer', '您好！我是AI简历助手，我将引导您一步步创建个人简历。让我们开始吧！'),
                'status': 'started'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'启动对话失败: {str(e)}'
            }
    
    def send_message(self, conversation_id: str, message: str, inputs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送消息到Dify Chatflow
        
        Args:
            conversation_id: 会话ID
            message: 用户消息
            inputs: 额外的输入参数
            
        Returns:
            Dify的响应结果
        """
        try:
            if conversation_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': '会话不存在或已过期'
                }
            
            session = self.active_sessions[conversation_id]
            session['last_activity'] = datetime.utcnow()
            
            # 发送消息到Dify工作流
            response = self._send_message_to_workflow(
                conversation_id=conversation_id,
                message=message,
                inputs=inputs or {}
            )
            
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
                'metadata': response.get('metadata', {})
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
        发送消息到Dify工作流
        
        Args:
            conversation_id: 会话ID
            message: 消息内容
            inputs: 输入参数
            
        Returns:
            Dify API响应
        """
        try:
            # Dify工作流API端点
            url = f"{self.dify_api_base}/workflows/run"
            
            headers = {
                'Authorization': f'Bearer {self.dify_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'inputs': {
                    'user_message': message,
                    'conversation_id': conversation_id,
                    **inputs
                },
                'response_mode': 'blocking',  # 同步模式
                'user': conversation_id,  # 使用conversation_id作为用户标识
                'workflow_id': self.workflow_id
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # 处理Dify响应格式
            if result.get('code') == 200 or 'data' in result:
                data = result.get('data', result)
                return {
                    'answer': data.get('outputs', {}).get('answer', data.get('answer', '')),
                    'metadata': data.get('metadata', {}),
                    'suggestions': data.get('outputs', {}).get('suggestions', [])
                }
            else:
                raise Exception(f"Dify API错误: {result.get('message', '未知错误')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"调用Dify API失败: {str(e)}")
    
    def _is_resume_complete(self, response: Dict) -> bool:
        """检查简历是否创建完成"""
        # 检查响应中是否包含完成标识
        answer = response.get('answer', '').lower()
        metadata = response.get('metadata', {})
        
        # 检查完成标识关键词
        completion_keywords = [
            '简历创建完成', '简历已生成', '简历制作完成',
            'resume complete', 'resume generated', '创建完毕'
        ]
        
        for keyword in completion_keywords:
            if keyword in answer:
                return True
        
        # 检查metadata中的完成标识
        if metadata.get('status') == 'completed' or metadata.get('resume_ready'):
            return True
        
        return False
    
    def _extract_resume_content(self, response: Dict) -> Optional[Dict]:
        """从响应中提取简历内容"""
        try:
            # 尝试从不同字段提取简历内容
            metadata = response.get('metadata', {})
            
            # 方式1: 从metadata中提取
            if 'resume_content' in metadata:
                return {
                    'markdown': metadata['resume_content'],
                    'title': metadata.get('resume_title', 'AI生成的简历')
                }
            
            # 方式2: 从answer中解析markdown格式
            answer = response.get('answer', '')
            if '# ' in answer or '## ' in answer:  # 包含markdown标题
                return {
                    'markdown': answer,
                    'title': 'AI生成的简历'
                }
            
            # 方式3: 检查outputs
            outputs = response.get('outputs', {})
            if 'resume_markdown' in outputs:
                return {
                    'markdown': outputs['resume_markdown'],
                    'title': outputs.get('resume_title', 'AI生成的简历')
                }
            
            return None
            
        except Exception as e:
            print(f"提取简历内容失败: {str(e)}")
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