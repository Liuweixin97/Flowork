import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Edit3, Download, Trash2, Eye, FileText, Clock, CheckSquare, Square, Plus, Bot } from 'lucide-react';
import { resumeAPI } from '../utils/api';
import { formatRelativeTime, downloadFile, truncate, cleanMarkdown } from '../utils/helpers';
import EmptyState from './EmptyState';
import ChatflowDialog from './ChatflowDialog';
import toast from 'react-hot-toast';

const ResumeList = () => {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [selectedResumes, setSelectedResumes] = useState(new Set());
  const [batchDeleteLoading, setBatchDeleteLoading] = useState(false);
  const [showChatflowDialog, setShowChatflowDialog] = useState(false);
  
  useEffect(() => {
    loadResumes();
  }, []);
  
  const loadResumes = async () => {
    try {
      setLoading(true);
      const response = await resumeAPI.getResumes();
      setResumes(response.data.resumes || []);
      setSelectedResumes(new Set()); // 清空选择
    } catch (error) {
      console.error('加载简历列表失败:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async (id, title) => {
    if (!window.confirm(`确定要删除简历"${title}"吗？此操作不可恢复。`)) {
      return;
    }
    
    try {
      setDeleteLoading(id);
      await resumeAPI.deleteResume(id);
      toast.success('简历删除成功');
      loadResumes();
    } catch (error) {
      console.error('删除简历失败:', error);
      toast.error('删除简历失败');
    } finally {
      setDeleteLoading(null);
    }
  };

  // 多选功能处理函数
  const handleSelectResume = (resumeId) => {
    const newSelected = new Set(selectedResumes);
    if (newSelected.has(resumeId)) {
      newSelected.delete(resumeId);
    } else {
      newSelected.add(resumeId);
    }
    setSelectedResumes(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedResumes.size === resumes.length) {
      setSelectedResumes(new Set());
    } else {
      setSelectedResumes(new Set(resumes.map(r => r.id)));
    }
  };

  const handleBatchDelete = async () => {
    const selectedCount = selectedResumes.size;
    if (selectedCount === 0) {
      toast.error('请先选择要删除的简历');
      return;
    }

    if (!window.confirm(`确定要删除选中的 ${selectedCount} 份简历吗？此操作不可恢复。`)) {
      return;
    }

    try {
      setBatchDeleteLoading(true);
      
      // 批量删除
      const deletePromises = Array.from(selectedResumes).map(id => 
        resumeAPI.deleteResume(id)
      );
      
      await Promise.all(deletePromises);
      
      toast.success(`成功删除 ${selectedCount} 份简历`);
      loadResumes();
    } catch (error) {
      console.error('批量删除失败:', error);
      toast.error('批量删除失败，请重试');
    } finally {
      setBatchDeleteLoading(false);
    }
  };
  
  const handleDownloadPDF = async (id, title) => {
    try {
      setDownloadLoading(id);
      const response = await resumeAPI.exportPDF(id);
      const filename = `${title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.pdf`;
      downloadFile(response.data, filename);
      toast.success('PDF导出成功');
    } catch (error) {
      console.error('PDF导出失败:', error);
    } finally {
      setDownloadLoading(null);
    }
  };

  const handleCreateNewResume = async () => {
    try {
      setCreateLoading(true);
      
      // 创建空白简历的默认内容
      const defaultMarkdown = `# 我的简历

## 个人信息
- 姓名: 
- 邮箱: 
- 电话: 
- 地址: 

## 工作经验

### 职位名称 | 公司名称 | 时间期间
- 工作职责描述
- 主要成就和贡献

## 教育背景

### 学位 | 学校名称 | 毕业时间
- 专业相关描述

## 技能
- 技能1
- 技能2
- 技能3

## 项目经验

### 项目名称 | 时间期间
- 项目描述
- 技术栈
- 个人贡献
`;

      const newResumeData = {
        resume_markdown: defaultMarkdown,
        title: `新建简历_${new Date().toLocaleDateString()}`
      };

      const response = await resumeAPI.createResume(newResumeData);
      
      if (response.data.success) {
        toast.success('空白简历创建成功！');
        navigate(`/edit/${response.data.resume_id}`);
      } else {
        toast.error('创建简历失败');
      }
    } catch (error) {
      console.error('创建简历失败:', error);
      toast.error('创建简历时发生错误');
    } finally {
      setCreateLoading(false);
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
      
      // 刷新列表以显示新创建的简历
      loadResumes();
      toast.success('简历创建完成，请在列表中查看');
    } catch (error) {
      console.error('处理生成的简历失败:', error);
      toast.error('简历创建过程出现问题');
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">加载中...</span>
      </div>
    );
  }
  
  if (resumes.length === 0) {
    return (
      <EmptyState 
        onCreateNew={handleCreateNewResume} 
        onAICreate={() => setShowChatflowDialog(true)}
        createLoading={createLoading} 
      />
    );
  }
  
  return (
    <div>
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">我的简历</h2>
            <p className="text-gray-600 mt-1">管理您的简历和使用浩流简历·flowork创建</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowChatflowDialog(true)}
              className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
            >
              <Bot className="h-4 w-4 mr-2" />
              浩流简历·flowork
            </button>
            <button
              onClick={handleCreateNewResume}
              disabled={createLoading}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {createLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Plus className="h-4 w-4 mr-2" />
              )}
              空白简历
            </button>
          </div>
        </div>
      </div>

      {/* 多选控制栏 */}
      {resumes.length > 0 && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleSelectAll}
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
              >
                {selectedResumes.size === resumes.length ? (
                  <CheckSquare className="h-4 w-4 mr-2 text-primary-600" />
                ) : (
                  <Square className="h-4 w-4 mr-2" />
                )}
                {selectedResumes.size === resumes.length ? '取消全选' : '全选'}
              </button>
              
              {selectedResumes.size > 0 && (
                <span className="text-sm text-gray-600">
                  已选择 {selectedResumes.size} 份简历
                </span>
              )}
            </div>
            
            {selectedResumes.size > 0 && (
              <button
                onClick={handleBatchDelete}
                disabled={batchDeleteLoading}
                className="inline-flex items-center px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors disabled:opacity-50"
              >
                {batchDeleteLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-700 mr-1"></div>
                ) : (
                  <Trash2 className="h-4 w-4 mr-1" />
                )}
                批量删除
              </button>
            )}
          </div>
        </div>
      )}
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {resumes.map((resume) => (
          <div key={resume.id} className={`card hover:shadow-md transition-all ${selectedResumes.has(resume.id) ? 'ring-2 ring-primary-500 bg-primary-50' : ''}`}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start space-x-3 flex-1">
                <button
                  onClick={() => handleSelectResume(resume.id)}
                  className="mt-1 text-gray-400 hover:text-primary-600 transition-colors"
                >
                  {selectedResumes.has(resume.id) ? (
                    <CheckSquare className="h-5 w-5 text-primary-600" />
                  ) : (
                    <Square className="h-5 w-5" />
                  )}
                </button>
                <h3 className="text-lg font-semibold text-gray-900 flex-1">
                  {resume.title}
                </h3>
              </div>
              <div className="flex items-center text-sm text-gray-500 ml-2">
                <Clock className="h-4 w-4 mr-1" />
                {formatRelativeTime(resume.created_at)}
              </div>
            </div>
            
            {resume.raw_markdown && (
              <div className="mb-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  {truncate(cleanMarkdown(resume.raw_markdown), 120)}
                </p>
              </div>
            )}
            
            <div className="flex items-center justify-between pt-4 border-t border-gray-100">
              <div className="flex space-x-2">
                <Link
                  to={`/edit/${resume.id}`}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-primary-100 text-primary-700 rounded-md hover:bg-primary-200 transition-colors"
                >
                  <Edit3 className="h-4 w-4 mr-1" />
                  编辑
                </Link>
                
                <button
                  onClick={() => handleDownloadPDF(resume.id, resume.title)}
                  disabled={downloadLoading === resume.id}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors disabled:opacity-50"
                >
                  {downloadLoading === resume.id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-700 mr-1"></div>
                  ) : (
                    <Download className="h-4 w-4 mr-1" />
                  )}
                  PDF
                </button>
              </div>
              
              <button
                onClick={() => handleDelete(resume.id, resume.title)}
                disabled={deleteLoading === resume.id}
                className="inline-flex items-center px-2 py-1.5 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors disabled:opacity-50"
              >
                {deleteLoading === resume.id ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-700"></div>
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
        ))}
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

export default ResumeList;