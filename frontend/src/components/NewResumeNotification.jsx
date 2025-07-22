import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, FileText, ArrowRight, ExternalLink } from 'lucide-react';
import toast from 'react-hot-toast';

const NewResumeNotification = ({ 
  isOpen, 
  onClose, 
  resumeData = null 
}) => {
  const navigate = useNavigate();
  const [isJumping, setIsJumping] = useState(false);

  if (!isOpen || !resumeData) return null;

  const handleJumpToEdit = () => {
    try {
      setIsJumping(true);
      
      // 跳转到编辑页面
      navigate(`/edit/${resumeData.resume_id}`, { replace: true });
      
      // 显示成功提示
      toast.success('正在打开简历编辑器...', {
        duration: 2000,
        position: 'top-center'
      });
      
      // 关闭弹窗
      onClose();
      
    } catch (error) {
      console.error('跳转到编辑页面失败:', error);
      toast.error('跳转失败，请重试');
    } finally {
      setIsJumping(false);
    }
  };

  const handleClose = () => {
    onClose();
    // 显示简历已保存的提示
    toast.success('简历已保存到列表中', {
      duration: 3000
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform transition-all">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <FileText className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                简历初稿已生成
              </h3>
              <p className="text-sm text-gray-600">
                浩流简历·flowork
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* 内容 */}
        <div className="p-6">
          <div className="mb-4">
            <p className="text-gray-700 mb-2">
              您的简历初稿已经生成完成！
            </p>
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">简历标题：</span>
                <span className="font-medium text-gray-900 truncate ml-2">
                  {resumeData.title || '未命名简历'}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">简历ID：</span>
                <span className="font-mono text-gray-700">
                  #{resumeData.resume_id}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-6">
            <p className="text-blue-800 text-sm">
              💡 您可以立即跳转到编辑器进行修改和完善，或稍后在简历列表中找到它。
            </p>
          </div>

          {/* 按钮组 */}
          <div className="flex flex-col space-y-3">
            <button
              onClick={handleJumpToEdit}
              disabled={isJumping}
              className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              {isJumping ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>跳转中...</span>
                </>
              ) : (
                <>
                  <ArrowRight className="h-4 w-4" />
                  <span>立即编辑简历</span>
                </>
              )}
            </button>
            
            <button
              onClick={handleClose}
              className="w-full flex items-center justify-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2.5 px-4 rounded-lg transition-colors"
            >
              <FileText className="h-4 w-4" />
              <span>稍后在列表中查看</span>
            </button>
          </div>
        </div>

        {/* 底部提示 */}
        <div className="px-6 py-4 bg-gray-50 rounded-b-lg">
          <p className="text-xs text-gray-600 text-center">
            简历已自动保存，您可以随时返回继续编辑
          </p>
        </div>
      </div>
    </div>
  );
};

export default NewResumeNotification;