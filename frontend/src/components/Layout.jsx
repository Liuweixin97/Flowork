import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText, Home, Plus } from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <FileText className="h-8 w-8 text-primary-600" />
                <span className="text-xl font-bold text-gray-900">简历编辑器</span>
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/') 
                    ? 'bg-primary-100 text-primary-700' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Home className="h-4 w-4" />
                <span>首页</span>
              </Link>
              
              <div className="text-sm text-gray-400">
                基于Dify的智能简历修改助手
              </div>
            </div>
          </div>
        </div>
      </nav>
      
      {/* 主要内容 */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
      
      {/* 页脚 */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-500 text-sm">
            <p>简历编辑器 - 配合Dify使用的智能简历修改工具</p>
            <p className="mt-1">
              Dify接收端点: <code className="bg-gray-100 px-2 py-1 rounded text-xs">POST http://localhost:8080/api/resumes/from-dify</code>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;