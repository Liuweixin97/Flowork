import React, { useState } from 'react';
import { Plus, FileText, Bot } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ResumeList from '../components/ResumeList';
import ChatflowDialog from '../components/ChatflowDialog';
import { useNavigate } from 'react-router-dom';
import { resumeAPI } from '../utils/api';

const ResumesPage = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [showChatflowDialog, setShowChatflowDialog] = useState(false);
  
  const handleChatflowClose = () => {
    setShowChatflowDialog(false);
  };
  
  const handleResumeGenerated = (resumeData) => {
    // 简历生成后的处理逻辑
    console.log('简历已生成:', resumeData);
    setShowChatflowDialog(false);
    // 跳转到编辑页面
    if (resumeData.resumeId) {
      navigate(`/edit/${resumeData.resumeId}`);
    }
  };

  const handleCreateBlankResume = async () => {
    try {
      // 创建基本简历框架模板，内容置空供用户填写
      const defaultMarkdown = `# 姓名

## 个人信息
- **姓名**: 
- **邮箱**: 
- **电话**: 
- **地址**: 
- **GitHub**: 
- **LinkedIn**: 

## 工作经验

### 职位名称 | 公司名称 | 时间段
- 工作内容描述...

## 教育背景

### 学位专业 | 学校名称 | 时间段
- **主修课程**: 
- **GPA**: 
- **相关活动**: 

## 技能特长
- **编程语言**: 
- **技术栈**: 
- **工具平台**: 

## 项目经验

### 项目名称 | 时间段
- **项目描述**: 
- **技术栈**: 
- **个人贡献**: 

## 获奖荣誉
- 

## 自我评价

`;

      const newResumeData = {
        raw_markdown: defaultMarkdown,
        title: `${user?.full_name || user?.username || '我'}的简历_${new Date().toLocaleDateString()}`
      };

      const response = await resumeAPI.createResume(newResumeData);
      
      if (response.data.success) {
        const { toast } = await import('react-hot-toast');
        toast.success('空白简历模板创建成功！');
        navigate(`/edit/${response.data.resume.id}`);
      } else {
        console.error('创建简历失败:', response.data.errors);
        const { toast } = await import('react-hot-toast');
        toast.error('创建简历失败，请重试');
      }
    } catch (error) {
      console.error('创建简历失败:', error);
      const { toast } = await import('react-hot-toast');
      toast.error('创建简历时发生错误，请重试');
    }
  };

  // 如果用户未登录，显示登录提示
  if (!isAuthenticated) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-12">
          <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">我的简历</h1>
          <p className="text-gray-600 mb-8">请先登录查看和管理您的简历</p>
          <div className="space-x-4">
            <a 
              href="/login" 
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              立即登录
            </a>
            <a 
              href="/register" 
              className="inline-flex items-center px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
            >
              注册账号
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">我的简历</h1>
            <p className="text-gray-600 mt-2">管理和编辑您的简历</p>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => setShowChatflowDialog(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Bot className="h-4 w-4 mr-2" />
              AI智能创建
            </button>
            
            <button
              onClick={handleCreateBlankResume}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              新建空白简历
            </button>
          </div>
        </div>
      </div>

      {/* 简历列表 */}
      <ResumeList />
      
      {/* AI对话弹窗 */}
      <ChatflowDialog
        isOpen={showChatflowDialog}
        onClose={handleChatflowClose}
        onResumeGenerated={handleResumeGenerated}
      />
    </div>
  );
};

export default ResumesPage;