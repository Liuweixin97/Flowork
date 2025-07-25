import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Edit3, Download, Trash2, Eye, FileText, Clock, CheckSquare, Square, Plus, Bot } from 'lucide-react';
import { resumeAPI } from '../utils/api';
import { formatRelativeTime, downloadFile, truncate, cleanMarkdown } from '../utils/helpers';
import { useAuth } from '../contexts/AuthContext';
import EmptyState from './EmptyState';
// ChatflowDialog moved to HomePage
import toast from 'react-hot-toast';

const ResumeList = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [selectedResumes, setSelectedResumes] = useState(new Set());
  const [batchDeleteLoading, setBatchDeleteLoading] = useState(false);
  // Chatflow dialog moved to HomePage
  
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
    // 检查用户是否已登录
    if (!isAuthenticated) {
      toast.error('请先登录后再创建简历', {
        duration: 4000,
      });
      // 跳转到登录页面
      navigate('/login', { 
        state: { 
          from: { pathname: '/' },
          message: '登录后即可创建简历'
        } 
      });
      return;
    }

    try {
      setCreateLoading(true);
      
      // 创建带有示例信息的简历模板
      const defaultMarkdown = `# 张三的简历

## 个人信息
- **姓名**: 张三
- **邮箱**: zhangsan@example.com
- **电话**: 138-0000-0000
- **地址**: 北京市朝阳区
- **GitHub**: https://github.com/zhangsan
- **LinkedIn**: https://linkedin.com/in/zhangsan

## 工作经验

### 高级前端开发工程师 | ABC科技有限公司 | 2021.03 - 至今
- 负责公司核心产品的前端架构设计和开发，使用React、TypeScript等技术栈
- 主导了用户界面重构项目，提升用户体验50%，页面加载速度提升30%
- 带领3人前端团队，建立代码规范和开发流程，提高团队开发效率
- 与产品和设计团队紧密合作，确保产品功能的高质量交付

### 前端开发工程师 | XYZ互联网公司 | 2019.07 - 2021.02
- 参与多个Web应用和移动端H5项目的开发和维护
- 使用Vue.js、React Native等技术开发跨平台应用
- 优化前端性能，减少50%的首屏加载时间
- 协助搭建前端自动化测试和CI/CD流程

## 教育背景

### 计算机科学与技术学士 | 清华大学 | 2015.09 - 2019.06
- **主修课程**: 数据结构、算法设计、软件工程、数据库原理
- **GPA**: 3.8/4.0
- **相关活动**: 计算机协会技术部部长，组织多次技术分享活动

## 技能特长
- **编程语言**: JavaScript/TypeScript, Python, Java
- **前端技术**: React, Vue.js, Angular, HTML5, CSS3, SASS/LESS
- **后端技术**: Node.js, Express, Django, Spring Boot
- **数据库**: MySQL, MongoDB, Redis
- **工具平台**: Git, Docker, Jenkins, AWS, 微信小程序

## 项目经验

### 企业级SaaS管理平台 | 2022.01 - 2022.12
- **项目描述**: 为中小企业提供一站式管理解决方案的Web平台
- **技术栈**: React, TypeScript, Ant Design, Node.js, MySQL
- **个人贡献**: 
  - 担任前端技术负责人，设计整体前端架构
  - 开发了可复用的组件库，提高开发效率40%
  - 实现了复杂的数据可视化功能和实时消息推送

### 移动端电商APP | 2020.06 - 2021.01
- **项目描述**: 面向年轻用户的社交电商移动应用
- **技术栈**: React Native, Redux, Node.js, MongoDB
- **个人贡献**:
  - 负责商品展示和购物车模块的开发
  - 优化用户体验，提升转化率15%
  - 集成第三方支付和物流接口

## 获奖荣誉
- 2022年度公司"最佳技术创新奖"
- 2021年"全国大学生程序设计竞赛"二等奖
- 2020年公司"优秀员工"称号

## 自我评价
热爱技术，具有强烈的学习能力和责任心。善于团队协作，能够在压力下保持高效工作。对用户体验有深入理解，注重代码质量和项目可维护性。持续关注前端技术发展趋势，乐于分享和交流技术心得。
`;

      const newResumeData = {
        raw_markdown: defaultMarkdown,
        title: `${user?.full_name || user?.username || '我'}的简历_${new Date().toLocaleDateString()}`
      };

      const response = await resumeAPI.createResume(newResumeData);
      
      if (response.data.success) {
        toast.success('简历模板创建成功！');
        navigate(`/edit/${response.data.resume.id}`);
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
      <>
        <EmptyState 
          onCreateNew={handleCreateNewResume} 
          createLoading={createLoading} 
        />
      </>
    );
  }
  
  return (
    <div>

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
      
      {/* ChatflowDialog已移至HomePage */}
    </div>
  );
};

export default ResumeList;