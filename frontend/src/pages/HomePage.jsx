import React, { useState } from 'react';
import { MessageCircle, FileText, Sparkles, Users, Zap, ArrowRight, Bot } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ResumeList from '../components/ResumeList';
import ChatflowDialog from '../components/ChatflowDialog';
import NewResumeNotification from '../components/NewResumeNotification';
import { useResumeNotification } from '../hooks/useResumeNotification';

const HomePage = () => {
  const { isAuthenticated } = useAuth();
  const [showChatflowDialog, setShowChatflowDialog] = useState(false);
  
  // 启用简历通知检查 - 监听Dify HTTP节点创建的新简历
  const { notification, closeNotification } = useResumeNotification(true);
  
  const handleChatflowClose = () => {
    setShowChatflowDialog(false);
  };
  
  const handleResumeGenerated = (resumeData) => {
    // 简历生成后的处理逻辑
    console.log('简历已生成:', resumeData);
    setShowChatflowDialog(false);
    // 可以在这里添加跳转到编辑页面的逻辑
  };
  
  return (
    <div className="space-y-12">
      {/* 主要入口区域 - 浩流简历对话 */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-8 text-center">
        <div className="max-w-3xl mx-auto">
          {/* 标题区域 */}
          <div className="flex items-center justify-center mb-4">
            <Bot className="h-12 w-12 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">浩流简历</h1>
          </div>
          
          <p className="text-xl text-gray-600 mb-6">
            与AI对话，智能创建专业简历
          </p>
          
          <p className="text-gray-500 mb-8 max-w-2xl mx-auto">
            告诉我你的工作经历、技能特长和求职意向，我将为你生成一份专业的简历。
            支持多轮对话优化，让你的简历更加出色。
          </p>
          
          {/* 主要CTA按钮 */}
          {isAuthenticated ? (
            <button
              onClick={() => setShowChatflowDialog(true)}
              className="inline-flex items-center px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105 duration-200"
            >
              <MessageCircle className="h-6 w-6 mr-3" />
              开始AI对话创建简历
              <ArrowRight className="h-5 w-5 ml-2" />
            </button>
          ) : (
            <div className="flex gap-4 justify-center">
              <a
                href="/login"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
              >
                立即登录
                <ArrowRight className="h-5 w-5 ml-2" />
              </a>
              <a
                href="/register"
                className="inline-flex items-center px-6 py-3 border-2 border-blue-600 text-blue-600 text-lg font-semibold rounded-lg hover:bg-blue-50 transition-colors"
              >
                免费注册
              </a>
            </div>
          )}
          
          {/* 特性介绍 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md border border-gray-100 transition-all duration-300 hover:-translate-y-1 group">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-200 transition-colors">
                <Sparkles className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2 text-center">智能优化</h3>
              <p className="text-gray-600 text-sm text-center leading-relaxed">AI根据行业特点和职位要求，智能优化简历内容和格式</p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md border border-gray-100 transition-all duration-300 hover:-translate-y-1 group">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-green-200 transition-colors">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2 text-center">多轮对话</h3>
              <p className="text-gray-600 text-sm text-center leading-relaxed">支持多轮对话交互，不断完善和调整简历细节</p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md border border-gray-100 transition-all duration-300 hover:-translate-y-1 group">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-200 transition-colors">
                <Zap className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2 text-center">快速生成</h3>
              <p className="text-gray-600 text-sm text-center leading-relaxed">几分钟内生成专业简历，支持PDF导出和在线编辑</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* 用户登录提示 */}
      {!isAuthenticated && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <div className="flex items-center justify-center mb-3">
            <FileText className="h-6 w-6 text-yellow-600 mr-2" />
            <h3 className="text-lg font-semibold text-yellow-800">提示</h3>
          </div>
          <p className="text-yellow-700 mb-4">
            登录后可以保存和管理你的简历，享受完整的简历编辑功能
          </p>
          <div className="space-x-4">
            <a 
              href="/login" 
              className="inline-flex items-center px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors"
            >
              立即登录
            </a>
            <a 
              href="/register" 
              className="inline-flex items-center px-4 py-2 border border-yellow-600 text-yellow-600 rounded-md hover:bg-yellow-50 transition-colors"
            >
              注册账号
            </a>
          </div>
        </div>
      )}
      
      {/* 已认证用户的快速访问 */}
      {isAuthenticated && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">快速访问</h2>
            <a 
              href="/resumes" 
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              查看我的简历 →
            </a>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => setShowChatflowDialog(true)}
              className="flex items-center justify-center p-4 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Bot className="h-6 w-6 mr-3" />
              <div className="text-left">
                <div className="font-medium">AI智能创建</div>
                <div className="text-sm text-blue-600">与AI对话生成简历</div>
              </div>
            </button>
            
            <a
              href="/resumes"
              className="flex items-center justify-center p-4 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <FileText className="h-6 w-6 mr-3" />
              <div className="text-left">
                <div className="font-medium">我的简历</div>
                <div className="text-sm text-gray-600">管理已有简历</div>
              </div>
            </a>
          </div>
        </div>
      )}
      
      {/* AI对话弹窗 */}
      <ChatflowDialog
        isOpen={showChatflowDialog}
        onClose={handleChatflowClose}
        onResumeGenerated={handleResumeGenerated}
      />
      
      {/* 新简历创建通知弹窗 */}
      <NewResumeNotification
        isOpen={!!notification}
        onClose={closeNotification}
        resumeData={notification}
      />
    </div>
  );
};

export default HomePage;