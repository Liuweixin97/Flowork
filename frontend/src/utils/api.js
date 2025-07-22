import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('[API Error]', error);
    
    if (error.response) {
      const message = error.response.data?.error || '请求失败';
      toast.error(message);
    } else if (error.request) {
      toast.error('网络连接失败，请检查后端服务是否启动');
    } else {
      toast.error('请求配置错误');
    }
    
    return Promise.reject(error);
  }
);

export const resumeAPI = {
  // 获取所有简历
  getResumes: () => api.get('/api/resumes'),
  
  // 获取特定简历
  getResume: (id) => api.get(`/api/resumes/${id}`),
  
  // 创建新简历
  createResume: (data) => api.post('/api/resumes/from-dify', data),
  
  // 更新简历
  updateResume: (id, data) => api.put(`/api/resumes/${id}`, data),
  
  // 删除简历
  deleteResume: (id) => api.delete(`/api/resumes/${id}`),
  
  // 导出PDF
  exportPDF: (id, smartOnepage = false) => api.get(`/api/resumes/${id}/pdf`, {
    responseType: 'blob',
    params: {
      smart_onepage: smartOnepage
    }
  }),
  
  // 预览HTML
  previewHTML: (id) => api.get(`/api/resumes/${id}/preview`),
  
  // 健康检查
  healthCheck: () => api.get('/api/health'),
};

export const chatflowAPI = {
  // 启动Chatflow对话
  startConversation: (userId = null) => api.post('/api/chatflow/start', { user_id: userId }),
  
  // 发送消息
  sendMessage: (conversationId, message, inputs = {}) => api.post('/api/chatflow/message', {
    conversation_id: conversationId,
    message,
    inputs
  }),
  
  // 获取对话历史
  getHistory: (conversationId) => api.get(`/api/chatflow/history/${conversationId}`),
  
  // 结束对话
  endConversation: (conversationId) => api.post('/api/chatflow/end', { 
    conversation_id: conversationId 
  }),
  
  // 从Chatflow结果手动创建简历
  createResumeFromChatflow: (markdownContent, title, conversationId) => api.post('/api/chatflow/create-resume', {
    markdown_content: markdownContent,
    title,
    conversation_id: conversationId
  }),
  
  // 检查Chatflow服务状态
  getStatus: () => api.get('/api/chatflow/status'),
};

export default api;