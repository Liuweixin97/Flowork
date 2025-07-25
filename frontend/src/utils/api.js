import axios from 'axios';
import toast from 'react-hot-toast';

// 动态检测API URL - 支持本地开发和内网穿透
const getApiBaseUrl = () => {
  // 如果设置了环境变量，直接使用
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // 根据当前访问的host动态决定API地址
  const currentHost = window.location.host;
  
  // 如果是通过花生壳访问
  if (currentHost.includes('vicp.fun')) {
    return 'http://23928mq418.vicp.fun:36218';
  }
  
  // 默认本地开发环境
  return 'http://localhost:8080';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 使api实例在全局可用，用于AuthContext
window.axios = api;

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

// 认证相关API
export const authAPI = {
  // 用户注册
  register: (data) => api.post('/api/auth/register', data),
  
  // 用户登录
  login: (data) => api.post('/api/auth/login', data),
  
  // 刷新token
  refreshToken: () => api.post('/api/auth/refresh'),
  
  // 用户登出
  logout: () => api.post('/api/auth/logout'),
  
  // 获取当前用户信息
  getCurrentUser: () => api.get('/api/auth/me'),
  
  // 更新用户资料
  updateProfile: (data) => api.put('/api/auth/profile', data),
  
  // 修改密码
  changePassword: (data) => api.post('/api/auth/change-password', data),
  
  // 检查用户名是否可用
  checkUsername: (username) => api.post('/api/auth/check-username', { username }),
  
  // 检查邮箱是否可用  
  checkEmail: (email) => api.post('/api/auth/check-email', { email }),
};

export const resumeAPI = {
  // 获取所有简历
  getResumes: () => api.get('/api/resumes'),
  
  // 获取特定简历
  getResume: (id) => api.get(`/api/resumes/${id}`),
  
  // 创建新简历
  createResume: (data) => api.post('/api/resumes', data),
  
  // 从Dify创建简历（向后兼容）
  createFromDify: (data) => api.post('/api/resumes/from-dify', data),
  
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

  // 使用HTML渲染方式导出PDF
  exportPDFHTML: (id, smartOnepage = false) => api.get(`/api/resumes/${id}/pdf-html`, {
    responseType: 'blob',
    params: {
      smart_onepage: smartOnepage
    }
  }),

  // 获取HTML内容（用于预览）
  getHTML: (id, smartOnepage = false) => api.get(`/api/resumes/${id}/html`, {
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
  // 启动Chatflow对话（需要认证）
  startConversation: () => api.post('/api/chatflow/start', {}),
  
  // 发送消息
  sendMessage: (conversationId, message, inputs = {}) => api.post('/api/chatflow/message', {
    conversation_id: conversationId,
    message,
    inputs
  }),

  // 发送流式消息
  sendStreamMessage: (conversationId, message, inputs = {}, onChunk, onComplete, onError) => {
    // 获取存储的访问token
    const accessToken = localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json',
    };
    
    // 如果有token，添加Authorization头
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    return fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/api/chatflow/stream`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message,
        inputs: inputs
      })
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      function readStream() {
        return reader.read().then(({ done, value }) => {
          if (done) {
            return;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                // 处理Dify标准SSE事件格式
                if (data.event === 'message') {
                  // 消息块事件
                  if (data.answer) {
                    onChunk(data.answer);
                  }
                } else if (data.event === 'message_end') {
                  // 消息结束事件
                  onComplete({
                    type: 'end',
                    status: 'completed',
                    metadata: data.metadata,
                    task_id: data.task_id,
                    message_id: data.message_id,
                    conversation_id: data.conversation_id
                  });
                  return;
                } else if (data.event === 'error') {
                  // Dify错误事件格式
                  const errorInfo = {
                    task_id: data.task_id,
                    message_id: data.message_id,
                    status: data.status,
                    code: data.code,
                    message: data.message,
                    event: 'error'
                  };
                  onError(new Error(data.message || '对话流处理出错'), errorInfo);
                  return;
                } else if (data.event === 'workflow_finished') {
                  // 工作流完成事件
                  const workflowData = data.data;
                  if (workflowData.status === 'failed') {
                    onError(new Error(workflowData.error || '工作流执行失败'), {
                      workflow_run_id: data.workflow_run_id,
                      error: workflowData.error,
                      status: workflowData.status
                    });
                    return;
                  }
                } else if (data.event === 'node_finished') {
                  // 节点完成事件，检查是否有失败的节点
                  const nodeData = data.data;
                  if (nodeData.status === 'failed') {
                    onError(new Error(nodeData.error || `节点 ${nodeData.title} 执行失败`), {
                      node_id: nodeData.node_id,
                      node_title: nodeData.title,
                      node_type: nodeData.node_type,
                      error: nodeData.error,
                      status: nodeData.status
                    });
                    return;
                  }
                }
                
                // 向后兼容原有格式
                if (data.type === 'chunk') {
                  onChunk(data.content);
                } else if (data.type === 'end') {
                  onComplete(data);
                  return;
                } else if (data.type === 'error') {
                  onError(new Error(data.error));
                  return;
                }
              } catch (e) {
                console.warn('Failed to parse streaming data:', e);
              }
            }
          }

          return readStream();
        });
      }

      return readStream();
    }).catch(onError);
  },
  
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