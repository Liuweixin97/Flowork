import React from 'react';
import ResumeList from '../components/ResumeList';
import { useAutoRedirect } from '../hooks/useAutoRedirect';

const HomePage = () => {
  // 启用自动跳转功能 - 监听Dify HTTP节点创建的新简历
  useAutoRedirect(true);
  
  return <ResumeList />;
};

export default HomePage;