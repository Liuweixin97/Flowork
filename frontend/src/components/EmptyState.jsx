import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Plus, Upload, Bot } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const EmptyState = ({ onCreateNew, createLoading = false }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const handleGoToHomepage = () => {
    navigate('/');
  };
  
  return (
    <div className="text-center py-16">
      <div className="mx-auto w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mb-6">
        <Bot className="h-12 w-12 text-blue-600" />
      </div>
      
      <h3 className="text-xl font-semibold text-gray-900 mb-3">
        还没有简历？
      </h3>
      
      <p className="text-gray-500 mb-8 max-w-md mx-auto leading-relaxed">
        推荐使用浩流简历AI智能生成，快速创建专业简历
      </p>
      
      <div className="space-y-4 max-w-sm mx-auto">
        {/* 推荐使用浩流简历 */}
        <button
          onClick={handleGoToHomepage}
          className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-xl"
        >
          <Bot className="h-5 w-5" />
          <span>使用浩流简历AI创建</span>
        </button>
        
        <div className="flex items-center justify-center space-x-4 text-gray-400">
          <div className="h-px bg-gray-300 flex-1"></div>
          <span className="text-sm">或</span>
          <div className="h-px bg-gray-300 flex-1"></div>
        </div>
        
        {/* 新建空白简历按钮 */}
        <button
          onClick={onCreateNew}
          disabled={createLoading}
          className="w-full flex items-center justify-center space-x-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 font-medium py-3 px-6 rounded-lg transition-colors duration-200"
        >
          {createLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-700"></div>
              <span>创建中...</span>
            </>
          ) : (
            <>
              <Plus className="h-5 w-5" />
              <span>新建空白简历</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default EmptyState;