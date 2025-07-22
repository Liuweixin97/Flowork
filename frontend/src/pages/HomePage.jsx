import React from 'react';
import ResumeList from '../components/ResumeList';
import NewResumeNotification from '../components/NewResumeNotification';
import { useResumeNotification } from '../hooks/useResumeNotification';

const HomePage = () => {
  // 启用简历通知检查 - 监听Dify HTTP节点创建的新简历
  const { notification, closeNotification } = useResumeNotification(true);
  
  return (
    <>
      <ResumeList />
      
      {/* 新简历创建通知弹窗 */}
      <NewResumeNotification
        isOpen={!!notification}
        onClose={closeNotification}
        resumeData={notification}
      />
    </>
  );
};

export default HomePage;