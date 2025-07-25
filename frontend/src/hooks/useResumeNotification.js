import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { resumeAPI } from '../utils/api';

/**
 * 简历通知Hook - 检查是否有新创建的简历需要显示通知弹窗
 */
export const useResumeNotification = (enabled = true) => {
  const location = useLocation();
  const [notification, setNotification] = useState(null);
  const [isCheckingNotification, setIsCheckingNotification] = useState(false);
  const intervalRef = useRef(null);
  
  // 检查简历通知
  const checkResumeNotification = async () => {
    if (isCheckingNotification) return;
    
    try {
      setIsCheckingNotification(true);
      
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/api/resume-notification`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success && result.notification) {
        console.log('[NOTIFICATION] 发现新简历通知:', result.notification);
        setNotification(result.notification);
        
        // 停止检查，等待用户处理通知
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
      
    } catch (error) {
      console.error('[NOTIFICATION] 检查通知失败:', error);
    } finally {
      setIsCheckingNotification(false);
    }
  };
  
  // 标记通知为已显示
  const markNotificationShown = async () => {
    try {
      await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/api/resume-notification`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      console.log('[NOTIFICATION] 通知已标记为已显示');
      
    } catch (error) {
      console.error('[NOTIFICATION] 标记通知失败:', error);
    }
  };
  
  // 关闭通知
  const closeNotification = async () => {
    await markNotificationShown();
    setNotification(null);
    
    // 重新开始检查（1分钟后）
    setTimeout(() => {
      if (enabled && location.pathname === '/') {
        startChecking();
      }
    }, 60000);
  };
  
  // 开始检查通知
  const startChecking = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    console.log('[NOTIFICATION] 开始检查简历通知');
    
    // 立即检查一次
    checkResumeNotification();
    
    // 每3秒检查一次
    intervalRef.current = setInterval(checkResumeNotification, 3000);
  };
  
  // 停止检查通知
  const stopChecking = () => {
    if (intervalRef.current) {
      console.log('[NOTIFICATION] 停止检查简历通知');
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };
  
  // 监听路由变化和启用状态
  useEffect(() => {
    if (!enabled) {
      stopChecking();
      return;
    }
    
    // 只在首页启用通知检查
    if (location.pathname === '/') {
      startChecking();
    } else {
      stopChecking();
      // 如果离开首页，清除当前通知
      setNotification(null);
    }
    
    return () => {
      stopChecking();
    };
  }, [enabled, location.pathname]);
  
  // 组件卸载时清理
  useEffect(() => {
    return () => {
      stopChecking();
    };
  }, []);
  
  return {
    notification,
    isCheckingNotification,
    closeNotification,
    markNotificationShown,
    isMonitoring: !!intervalRef.current
  };
};

export default useResumeNotification;