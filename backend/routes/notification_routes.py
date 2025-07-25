from flask import Blueprint, Response, request
import json
import time
from datetime import datetime
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notification_bp = Blueprint('notification', __name__)

# 全局事件队列，存储需要推送给前端的事件
event_queues = {}  # client_id -> queue
event_queues_lock = threading.Lock()

class NotificationService:
    """通知服务 - 负责向前端推送实时事件"""
    
    @staticmethod
    def add_client(client_id):
        """添加新的客户端连接"""
        with event_queues_lock:
            if client_id not in event_queues:
                event_queues[client_id] = queue.Queue()
                logger.info(f"添加SSE客户端: {client_id}")
    
    @staticmethod
    def remove_client(client_id):
        """移除客户端连接"""
        with event_queues_lock:
            if client_id in event_queues:
                del event_queues[client_id]
                logger.info(f"移除SSE客户端: {client_id}")
    
    @staticmethod
    def broadcast_event(event_type, data):
        """广播事件到所有连接的客户端"""
        event_data = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        with event_queues_lock:
            for client_id, event_queue in event_queues.items():
                try:
                    event_queue.put_nowait(event_data)
                    logger.info(f"事件推送给客户端 {client_id}: {event_type}")
                except queue.Full:
                    logger.warning(f"客户端队列已满: {client_id}")
    
    @staticmethod
    def broadcast_resume_created(resume_id, title, redirect_url):
        """广播简历创建事件"""
        NotificationService.broadcast_event('resume_created', {
            'resume_id': resume_id,
            'title': title,
            'redirect_url': redirect_url,
            'auto_redirect': True
        })

@notification_bp.route('/api/notifications/events')
def events():
    """SSE端点 - 向前端推送实时事件"""
    
    # 生成客户端ID
    client_id = request.headers.get('X-Client-ID', f'client_{int(time.time() * 1000)}')
    
    def event_stream():
        # 添加客户端
        NotificationService.add_client(client_id)
        
        try:
            # 发送连接确认
            yield f"data: {json.dumps({'type': 'connected', 'client_id': client_id})}\\n\\n"
            
            # 获取客户端的事件队列
            client_queue = event_queues.get(client_id)
            if not client_queue:
                return
            
            # 持续监听事件队列
            while True:
                try:
                    # 等待事件，设置超时避免长时间阻塞
                    event_data = client_queue.get(timeout=30)
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\\n\\n"
                    
                except queue.Empty:
                    # 发送心跳保持连接
                    yield f"data: {json.dumps({'type': 'ping', 'timestamp': datetime.utcnow().isoformat()})}\\n\\n"
                    
                except Exception as e:
                    logger.error(f"事件流错误: {e}")
                    break
                    
        finally:
            # 清理客户端连接
            NotificationService.remove_client(client_id)
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, X-Client-ID',
        }
    )

@notification_bp.route('/api/notifications/test', methods=['POST'])
def test_notification():
    """测试通知功能"""
    try:
        data = request.get_json() or {}
        event_type = data.get('type', 'test')
        message = data.get('message', '测试消息')
        
        NotificationService.broadcast_event(event_type, {'message': message})
        
        return {
            'success': True,
            'message': f'测试事件已发送: {event_type}'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

# 导出通知服务供其他模块使用
__all__ = ['notification_bp', 'NotificationService']