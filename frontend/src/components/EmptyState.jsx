import React from 'react';
import { FileText, Plus, Upload, Bot } from 'lucide-react';

const EmptyState = ({ onCreateNew, onAICreate, createLoading = false }) => {
  return (
    <div className="text-center py-16">
      <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
        <FileText className="h-12 w-12 text-gray-400" />
      </div>
      
      <h3 className="text-xl font-semibold text-gray-900 mb-3">
        暂无简历
      </h3>
      
      <p className="text-gray-500 mb-8 max-w-md mx-auto leading-relaxed">
        您还没有任何简历。可以通过以下方式开始创建您的第一份简历：
      </p>
      
      <div className="space-y-4 max-w-sm mx-auto">
        {/* AI创建简历按钮 */}
        <button
          onClick={onAICreate}
          className="w-full flex items-center justify-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
        >
          <Bot className="h-5 w-5" />
          <span>AI智能创建简历</span>
        </button>
        
        {/* 新建空白简历按钮 */}
        <button
          onClick={onCreateNew}
          disabled={createLoading}
          className="w-full flex items-center justify-center space-x-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
        >
          {createLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>创建中...</span>
            </>
          ) : (
            <>
              <Plus className="h-5 w-5" />
              <span>新建空白简历</span>
            </>
          )}
        </button>
        
        {/* Dify集成说明 */}
        <div className="border-t pt-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Upload className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-left">
                <h4 className="font-medium text-blue-900 mb-1">
                  从Dify导入简历
                </h4>
                <p className="text-sm text-blue-800 leading-relaxed">
                  在Dify中生成简历后，通过HTTP节点发送到本服务，简历将自动出现在此列表中
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 配置信息 */}
      <div className="mt-12 bg-gray-50 border border-gray-200 rounded-lg p-6 max-w-2xl mx-auto">
        <h4 className="font-medium text-gray-900 mb-3">Dify HTTP节点配置</h4>
        <div className="text-sm text-gray-700 space-y-2 text-left">
          <div><strong>方法:</strong> POST</div>
          <div><strong>URL:</strong> <code className="bg-gray-200 px-2 py-1 rounded">http://host.docker.internal:8080/api/resumes/from-dify</code></div>
          <div><strong>请求头:</strong> <code className="bg-gray-200 px-2 py-1 rounded">Content-Type: application/json</code></div>
          <div><strong>请求体:</strong></div>
          <pre className="bg-gray-200 p-3 rounded text-xs overflow-x-auto">
{`{
  "resume_markdown": "{{LLM生成的简历内容}}",
  "title": "{{简历标题}}"
}`}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default EmptyState;