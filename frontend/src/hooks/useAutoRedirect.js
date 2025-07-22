import { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { resumeAPI } from '../utils/api';
import toast from 'react-hot-toast';

/**
 * 自动跳转Hook - 检测新创建的简历并自动跳转到编辑页面
 * 当Dify HTTP节点创建简历后，前端自动跳转到该简历的编辑页面
 */
export const useAutoRedirect = (enabled = true) => {
  const navigate = useNavigate();
  const location = useLocation();
  const intervalRef = useRef(null);
  const lastCheckTimeRef = useRef(Date.now());
  const isCheckingRef = useRef(false);
  
  useEffect(() => {
    if (!enabled) return;
    
    // 只在首页启用自动跳转检查
    if (location.pathname !== '/') return;
    
    const checkForNewResume = async () => {
      // 防止并发请求
      if (isCheckingRef.current) return;
      
      try {
        isCheckingRef.current = true;
        
        // 获取简历列表
        const response = await resumeAPI.getResumes();
        const resumes = response.data.resumes || [];
        
        if (resumes.length === 0) {
          return;
        }
        
        // 找到最新的简历（按创建时间排序）
        const latestResume = resumes[0]; // API已经按updated_at desc排序
        const resumeCreateTime = new Date(latestResume.created_at).getTime();
        const lastCheckTime = lastCheckTimeRef.current;
        
        // 如果最新简历是在上次检查后创建的，则自动跳转
        if (resumeCreateTime > lastCheckTime) {
          console.log('[AUTO_REDIRECT] 检测到新简历:', {
            id: latestResume.id,
            title: latestResume.title,
            created_at: latestResume.created_at,
            lastCheckTime: new Date(lastCheckTime).toISOString()
          });
          
          // 显示通知
          toast.success(`新简历已创建: ${latestResume.title}`, {
            duration: 3000,
            position: 'top-center',
          });
          
          // 延迟跳转，让用户看到通知
          setTimeout(() => {
            navigate(`/edit/${latestResume.id}`, { replace: true });
            toast.success('已自动跳转到简历编辑页面', {
              duration: 2000,
            });
          }, 1500);
          
          // 清除定时器，避免重复跳转
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
        
      } catch (error) {
        console.error('[AUTO_REDIRECT] 检查新简历失败:', error);
      } finally {
        isCheckingRef.current = false;
      }
    };
    
    // 开始定期检查（每2秒检查一次）
    console.log('[AUTO_REDIRECT] 开始监听新简历创建');
    intervalRef.current = setInterval(checkForNewResume, 2000);
    
    // 立即执行一次检查
    checkForNewResume();
    
    // 清理函数
    return () => {
      if (intervalRef.current) {
        console.log('[AUTO_REDIRECT] 停止监听新简历创建');
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      isCheckingRef.current = false;
    };
  }, [enabled, location.pathname, navigate]);
  
  // 更新最后检查时间（当组件挂载时）
  useEffect(() => {
    lastCheckTimeRef.current = Date.now();
  }, [location.pathname]);
  
  return {
    isMonitoring: !!intervalRef.current
  };
};

export default useAutoRedirect;