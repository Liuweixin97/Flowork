import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../utils/api';
import toast from 'react-hot-toast';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth必须在AuthProvider内使用');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Token管理
  const setTokens = (accessToken, refreshToken) => {
    if (accessToken) {
      localStorage.setItem('access_token', accessToken);
      // 设置axios默认授权头
      if (window.axios) {
        window.axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      }
    }
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
  };

  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    // 清除axios默认授权头
    if (window.axios) {
      delete window.axios.defaults.headers.common['Authorization'];
    }
  };

  const getAccessToken = () => {
    return localStorage.getItem('access_token');
  };

  const getRefreshToken = () => {
    return localStorage.getItem('refresh_token');
  };

  // 登录
  const login = async (loginData) => {
    try {
      const response = await authAPI.login(loginData);
      
      if (response.data.success) {
        const { user: userData, access_token, refresh_token } = response.data;
        
        setTokens(access_token, refresh_token);
        setUser(userData);
        setIsAuthenticated(true);
        
        toast.success(`欢迎回来，${userData.full_name || userData.username}！`);
        return { success: true, user: userData };
      } else {
        return { success: false, errors: response.data.errors || ['登录失败'] };
      }
    } catch (error) {
      console.error('登录错误:', error);
      const errors = error.response?.data?.errors || ['登录失败，请稍后重试'];
      return { success: false, errors };
    }
  };

  // 注册
  const register = async (registerData) => {
    try {
      const response = await authAPI.register(registerData);
      
      if (response.data.success) {
        const { user: userData, access_token, refresh_token } = response.data;
        
        setTokens(access_token, refresh_token);
        setUser(userData);
        setIsAuthenticated(true);
        
        toast.success(`注册成功，欢迎 ${userData.full_name || userData.username}！`);
        return { success: true, user: userData };
      } else {
        return { success: false, errors: response.data.errors || ['注册失败'] };
      }
    } catch (error) {
      console.error('注册错误:', error);
      const errors = error.response?.data?.errors || ['注册失败，请稍后重试'];
      return { success: false, errors };
    }
  };

  // 登出
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('登出请求失败:', error);
    } finally {
      clearTokens();
      setUser(null);
      setIsAuthenticated(false);
      toast.success('已安全登出');
    }
  };

  // 刷新token
  const refreshAccessToken = async () => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw new Error('没有刷新token');
      }

      // 临时设置refresh token用于请求
      const originalAuth = window.axios?.defaults.headers.common['Authorization'];
      if (window.axios) {
        window.axios.defaults.headers.common['Authorization'] = `Bearer ${refreshToken}`;
      }

      const response = await authAPI.refreshToken();
      
      if (response.data.success) {
        const { access_token, user: userData } = response.data;
        setTokens(access_token, null); // 只更新access token
        setUser(userData);
        setIsAuthenticated(true);
        return true;
      } else {
        throw new Error('刷新token失败');
      }
    } catch (error) {
      console.error('刷新token失败:', error);
      clearTokens();
      setUser(null);
      setIsAuthenticated(false);
      return false;
    }
  };

  // 获取用户信息
  const fetchUser = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      
      if (response.data.success) {
        setUser(response.data.user);
        setIsAuthenticated(true);
        return true;
      } else {
        throw new Error('获取用户信息失败');
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
      
      // 尝试刷新token
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        clearTokens();
        setUser(null);
        setIsAuthenticated(false);
      }
      return false;
    }
  };

  // 更新用户资料
  const updateProfile = async (profileData) => {
    try {
      const response = await authAPI.updateProfile(profileData);
      
      if (response.data.success) {
        setUser(response.data.user);
        toast.success('资料更新成功');
        return { success: true };
      } else {
        return { success: false, errors: response.data.errors || ['更新失败'] };
      }
    } catch (error) {
      console.error('更新资料失败:', error);
      const errors = error.response?.data?.errors || ['更新失败，请稍后重试'];
      return { success: false, errors };
    }
  };

  // 修改密码
  const changePassword = async (passwordData) => {
    try {
      const response = await authAPI.changePassword(passwordData);
      
      if (response.data.success) {
        toast.success('密码修改成功');
        return { success: true };
      } else {
        return { success: false, errors: response.data.errors || ['密码修改失败'] };
      }
    } catch (error) {
      console.error('修改密码失败:', error);
      const errors = error.response?.data?.errors || ['密码修改失败，请稍后重试'];
      return { success: false, errors };
    }
  };

  // 初始化认证状态
  useEffect(() => {
    const initAuth = async () => {
      const token = getAccessToken();
      
      if (token) {
        // 设置axios默认授权头
        if (window.axios) {
          window.axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
        
        // 获取用户信息
        await fetchUser();
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  // 设置axios拦截器处理token过期
  useEffect(() => {
    if (!window.axios) return;

    const responseInterceptor = window.axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const original = error.config;

        if (error.response?.status === 401 && !original._retry) {
          original._retry = true;

          const refreshed = await refreshAccessToken();
          if (refreshed) {
            // 重试原始请求
            return window.axios(original);
          }
        }

        return Promise.reject(error);
      }
    );

    return () => {
      window.axios.interceptors.response.eject(responseInterceptor);
    };
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    fetchUser,
    refreshAccessToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};