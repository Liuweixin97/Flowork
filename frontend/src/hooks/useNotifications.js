import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

/**
 * 实时通知Hook - 监听后端SSE事件并自动处理跳转
 */
export const useNotifications = (enabled = true) => {
  const navigate = useNavigate();
  const eventSourceRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);
  
  const clientId = useRef(`client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  useEffect(() => {
    if (!enabled) return;
    
    const connectSSE = () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
        const sseUrl = `${apiUrl}/api/notifications/events`;
        
        console.log('[SSE] 建立连接:', sseUrl);
        
        const eventSource = new EventSource(sseUrl);
        eventSourceRef.current = eventSource;
        
        // 连接成功
        eventSource.onopen = () => {
          console.log('[SSE] 连接已建立');
          setIsConnected(true);
        };
        
        // 接收消息
        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('[SSE] 收到事件:', data);
            
            setLastEvent(data);
            handleNotificationEvent(data);
            
          } catch (error) {
            console.error('[SSE] 事件解析失败:', error);
          }
        };
        
        // 连接错误
        eventSource.onerror = (error) => {
          console.error('[SSE] 连接错误:', error);
          setIsConnected(false);
          
          // 3秒后重连
          setTimeout(() => {
            if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
              console.log('[SSE] 尝试重新连接...');
              connectSSE();
            }
          }, 3000);
        };
        
      } catch (error) {
        console.error('[SSE] 建立连接失败:', error);
      }
    };
    
    // 处理通知事件
    const handleNotificationEvent = (data) => {
      const { type, data: eventData, timestamp } = data;
      
      switch (type) {
        case 'connected':
          console.log('[SSE] 连接确认:', eventData);
          break;
          
        case 'resume_created':
          handleResumeCreated(eventData);
          break;
          
        case 'ping':
          // 心跳，忽略
          break;
          
        default:
          console.log('[SSE] 未知事件类型:', type, eventData);
      }
    };
    
    // 处理简历创建事件
    const handleResumeCreated = (resumeData) => {
      const { resume_id, title, redirect_url, auto_redirect } = resumeData;
      
      console.log('[SSE] 简历创建事件:', resumeData);
      
      // 显示通知
      toast.success(`新简历已创建: ${title}`, {
        duration: 4000,
        position: 'top-center',
      });
      
      // 自动跳转到编辑页面
      if (auto_redirect && resume_id) {
        console.log(`[SSE] 自动跳转到编辑页面: /edit/${resume_id}`);
        
        // 延迟跳转，让用户看到通知
        setTimeout(() => {
          navigate(`/edit/${resume_id}`, { replace: true });
          toast.success('已自动跳转到简历编辑页面', {
            duration: 3000,
          });
        }, 1000);
      }
    };
    
    // 建立连接
    connectSSE();
    
    // 清理函数
    return () => {
      if (eventSourceRef.current) {
        console.log('[SSE] 关闭连接');
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      setIsConnected(false);
    };
  }, [enabled, navigate]);
  
  // 手动发送测试事件（用于调试）
  const sendTestNotification = async (type = 'test', message = '测试消息') => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      const response = await fetch(`${apiUrl}/api/notifications/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type, message }),
      });
      
      const result = await response.json();
      console.log('测试通知发送结果:', result);
      
      if (result.success) {
        toast.success('测试通知已发送');
      } else {
        toast.error('测试通知发送失败');
      }
      
      return result;
    } catch (error) {
      console.error('发送测试通知失败:', error);
      toast.error('发送测试通知失败');
      return { success: false, error: error.message };
    }
  };
  
  return {
    isConnected,
    lastEvent,
    clientId: clientId.current,
    sendTestNotification,
  };
};

export default useNotifications;