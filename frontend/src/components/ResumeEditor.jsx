import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, Download, ArrowLeft, Eye, EyeOff, RefreshCw, ChevronDown, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { resumeAPI } from '../utils/api';
import { formatDate, downloadFile, debounce } from '../utils/helpers';
import toast from 'react-hot-toast';
import ChatflowDialog from './ChatflowDialog';

const ResumeEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [showPreview, setShowPreview] = useState(true);
  const [title, setTitle] = useState('');
  const [markdown, setMarkdown] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [lastSaveTime, setLastSaveTime] = useState(0);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showChatflowDialog, setShowChatflowDialog] = useState(false);
  
  const exportMenuRef = useRef(null);
  
  // 自动保存防抖
  const debouncedSave = debounce(async (newTitle, newMarkdown) => {
    if (!resume || (!newTitle && !newMarkdown)) return;
    
    try {
      const updateData = {};
      if (newTitle !== resume.title) updateData.title = newTitle;
      if (newMarkdown !== resume.raw_markdown) updateData.raw_markdown = newMarkdown;
      
      if (Object.keys(updateData).length > 0) {
        await resumeAPI.updateResume(id, updateData);
        setHasUnsavedChanges(false);
        toast.success('自动保存成功', { duration: 1000 });
      }
    } catch (error) {
      console.error('自动保存失败:', error);
    }
  }, 5000);
  
  useEffect(() => {
    loadResume();
  }, [id]);
  
  useEffect(() => {
    if (resume && (title !== resume.title || markdown !== resume.raw_markdown)) {
      setHasUnsavedChanges(true);
      debouncedSave(title, markdown);
    }
  }, [title, markdown, resume]);
  
  // 防止用户意外离开
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);
  
  // 处理导出菜单外部点击关闭
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target)) {
        setShowExportMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  const loadResume = async () => {
    try {
      setLoading(true);
      const response = await resumeAPI.getResume(id);
      const resumeData = response.data.resume;
      setResume(resumeData);
      setTitle(resumeData.title || '');
      setMarkdown(resumeData.raw_markdown || '');
    } catch (error) {
      console.error('加载简历失败:', error);
      toast.error('简历加载失败');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSave = async () => {
    try {
      setSaving(true);
      const updateData = {
        title,
        raw_markdown: markdown
      };
      
      await resumeAPI.updateResume(id, updateData);
      setHasUnsavedChanges(false);
      toast.success('保存成功');
      
      // 更新本地resume状态
      setResume(prev => ({
        ...prev,
        title,
        raw_markdown: markdown,
        updated_at: new Date().toISOString()
      }));
    } catch (error) {
      console.error('保存失败:', error);
    } finally {
      setSaving(false);
    }
  };
  
  const handleDownloadPDF = async (smartOnepage = false) => {
    try {
      setDownloading(true);
      setShowExportMenu(false);
      
      const response = await resumeAPI.exportPDF(id, smartOnepage);
      const suffix = smartOnepage ? '_智能一页' : '';
      const filename = `${title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}${suffix}.pdf`;
      downloadFile(response.data, filename);
      
      const successMsg = smartOnepage ? 'PDF智能一页导出成功' : 'PDF导出成功';
      toast.success(successMsg);
    } catch (error) {
      console.error('PDF导出失败:', error);
      toast.error('PDF导出失败');
    } finally {
      setDownloading(false);
    }
  };
  
  const handleBack = () => {
    if (hasUnsavedChanges) {
      if (window.confirm('有未保存的更改，确定要离开吗？')) {
        navigate('/');
      }
    } else {
      navigate('/');
    }
  };
  
  const handleResumeGenerated = (generatedResume) => {
    try {
      // 如果有简历ID，直接跳转到编辑页面
      if (generatedResume.resumeId) {
        navigate(`/edit/${generatedResume.resumeId}`);
        toast.success('简历已创建，正在跳转到编辑页面');
        return;
      }
      
      // 如果有简历内容，更新当前编辑器
      if (generatedResume.content) {
        const newMarkdown = generatedResume.content.markdown || generatedResume.content;
        const newTitle = generatedResume.content.title || 'AI生成的简历';
        
        setMarkdown(newMarkdown);
        setTitle(newTitle);
        setHasUnsavedChanges(true);
        
        toast.success('简历内容已导入编辑器，请预览并调整');
      }
    } catch (error) {
      console.error('处理生成的简历失败:', error);
      toast.error('简历内容导入失败');
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">加载简历中...</span>
      </div>
    );
  }
  
  if (!resume) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">简历未找到</p>
      </div>
    );
  }
  
  return (
    <div className="max-w-none">
      {/* 工具栏 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBack}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>返回</span>
            </button>
            
            <div className="h-6 w-px bg-gray-300"></div>
            
            <div>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="text-lg font-semibold bg-transparent border-none outline-none focus:ring-0 p-0 text-gray-900"
                placeholder="输入简历标题..."
              />
              {resume.updated_at && (
                <p className="text-sm text-gray-500">
                  最后更新: {formatDate(resume.updated_at)}
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {hasUnsavedChanges && (
              <span className="text-sm text-orange-600 flex items-center">
                <RefreshCw className="h-4 w-4 mr-1" />
                有未保存的更改
              </span>
            )}
            
            <button
              onClick={() => setShowChatflowDialog(true)}
              className="flex items-center space-x-1 px-3 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
            >
              <Bot className="h-4 w-4" />
              <span>AI助手</span>
            </button>
            
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="flex items-center space-x-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              {showPreview ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              <span>{showPreview ? '隐藏预览' : '显示预览'}</span>
            </button>
            
            <button
              onClick={handleSave}
              disabled={saving || !hasUnsavedChanges}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              <span>{saving ? '保存中...' : '保存'}</span>
            </button>
            
            <div className="relative" ref={exportMenuRef}>
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                disabled={downloading}
                className="flex items-center space-x-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
              >
                {downloading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <Download className="h-4 w-4" />
                )}
                <span>{downloading ? '导出中...' : '导出PDF'}</span>
                <ChevronDown className="h-4 w-4" />
              </button>
              
              {showExportMenu && !downloading && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                  <div className="py-1">
                    <button
                      onClick={() => handleDownloadPDF(false)}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      普通PDF导出
                    </button>
                    <button
                      onClick={() => handleDownloadPDF(true)}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      智能一页导出
                    </button>
                  </div>
                  <div className="border-t border-gray-100 px-4 py-2">
                    <p className="text-xs text-gray-500">
                      智能一页：自动调整字号和间距，确保内容适合一页A4纸
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* 编辑器区域 */}
      <div className={`grid gap-6 ${showPreview ? 'lg:grid-cols-2' : 'grid-cols-1'}`}>
        {/* Markdown编辑器 */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-700">Markdown编辑器</h3>
          </div>
          <div className="p-0">
            <textarea
              value={markdown}
              onChange={(e) => setMarkdown(e.target.value)}
              className="w-full h-screen max-h-[600px] p-4 border-none resize-none focus:outline-none focus:ring-0 font-mono text-sm leading-relaxed"
              placeholder="请输入简历的Markdown内容..."
              style={{ minHeight: '500px' }}
            />
          </div>
        </div>
        
        {/* 预览区域 */}
        {showPreview && (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-700">实时预览</h3>
            </div>
            <div className="p-6 overflow-auto" style={{ maxHeight: '600px' }}>
              <div className="markdown-preview">
                <ReactMarkdown>{markdown || '预览区域将显示Markdown渲染后的内容...'}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* 提示信息 */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">编辑提示:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• 支持标准Markdown语法，包括标题、列表、粗体、斜体等</li>
          <li>• 内容会自动保存，无需担心丢失</li>
          <li>• 可以随时导出为精美的PDF格式</li>
          <li>• 使用右侧预览查看最终效果</li>
        </ul>
      </div>
      
      {/* Chatflow Dialog */}
      <ChatflowDialog 
        isOpen={showChatflowDialog}
        onClose={() => setShowChatflowDialog(false)}
        onResumeGenerated={handleResumeGenerated}
      />
    </div>
  );
};

export default ResumeEditor;