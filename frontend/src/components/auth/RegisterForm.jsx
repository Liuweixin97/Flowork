import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { UserPlus, Eye, EyeOff, User, Mail, Lock, Loader, Check, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { authAPI } from '../../utils/api';

const RegisterForm = ({ onSuccess }) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState([]);
  const [validation, setValidation] = useState({
    username: { available: null, checking: false },
    email: { available: null, checking: false }
  });

  // 防抖检查用户名可用性
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (formData.username.length >= 3) {
        setValidation(prev => ({
          ...prev,
          username: { ...prev.username, checking: true }
        }));
        
        try {
          const response = await authAPI.checkUsername(formData.username);
          setValidation(prev => ({
            ...prev,
            username: {
              available: response.data.available,
              checking: false,
              message: response.data.message
            }
          }));
        } catch (error) {
          setValidation(prev => ({
            ...prev,
            username: { available: null, checking: false }
          }));
        }
      } else {
        setValidation(prev => ({
          ...prev,
          username: { available: null, checking: false }
        }));
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [formData.username]);

  // 防抖检查邮箱可用性
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (formData.email.includes('@')) {
        setValidation(prev => ({
          ...prev,
          email: { ...prev.email, checking: true }
        }));
        
        try {
          const response = await authAPI.checkEmail(formData.email);
          setValidation(prev => ({
            ...prev,
            email: {
              available: response.data.available,
              checking: false,
              message: response.data.message
            }
          }));
        } catch (error) {
          setValidation(prev => ({
            ...prev,
            email: { available: null, checking: false }
          }));
        }
      } else {
        setValidation(prev => ({
          ...prev,
          email: { available: null, checking: false }
        }));
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [formData.email]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 清除错误信息
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  const validateForm = () => {
    const newErrors = [];

    // 用户名验证
    if (!formData.username.trim()) {
      newErrors.push('用户名不能为空');
    } else if (formData.username.length < 3) {
      newErrors.push('用户名长度至少3个字符');
    } else if (validation.username.available === false) {
      newErrors.push('用户名已存在');
    }

    // 邮箱验证
    if (!formData.email.trim()) {
      newErrors.push('邮箱不能为空');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.push('邮箱格式不正确');
    } else if (validation.email.available === false) {
      newErrors.push('邮箱已被使用');
    }

    // 密码验证
    if (!formData.password) {
      newErrors.push('密码不能为空');
    } else if (formData.password.length < 6) {
      newErrors.push('密码长度至少6位');
    }

    // 确认密码验证
    if (formData.password !== formData.confirmPassword) {
      newErrors.push('两次输入的密码不一致');
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    setErrors([]);

    try {
      const result = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || formData.username
      });
      
      if (result.success) {
        if (onSuccess) {
          onSuccess(result.user);
        }
      } else {
        setErrors(result.errors || ['注册失败']);
      }
    } catch (error) {
      setErrors(['注册过程中发生错误，请稍后重试']);
    } finally {
      setLoading(false);
    }
  };

  const renderValidationIcon = (field) => {
    const fieldValidation = validation[field];
    
    if (fieldValidation.checking) {
      return <Loader className="h-4 w-4 animate-spin text-gray-400" />;
    } else if (fieldValidation.available === true) {
      return <Check className="h-4 w-4 text-green-500" />;
    } else if (fieldValidation.available === false) {
      return <X className="h-4 w-4 text-red-500" />;
    }
    
    return null;
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-xl rounded-2xl p-8">
        {/* 头部 */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center mb-4">
            <UserPlus className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">创建账户</h2>
          <p className="text-gray-600 mt-2">加入浩流简历，开始创建专业简历</p>
        </div>

        {/* 错误信息 */}
        {errors.length > 0 && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <ul className="text-sm text-red-600 space-y-1">
              {errors.map((error, index) => (
                <li key={index} className="flex items-center">
                  <span className="w-1.5 h-1.5 bg-red-400 rounded-full mr-2"></span>
                  {error}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 注册表单 */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* 用户名 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              用户名 *
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="输入用户名"
                disabled={loading}
                autoComplete="username"
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                {renderValidationIcon('username')}
              </div>
            </div>
            {validation.username.message && (
              <p className={`text-xs mt-1 ${validation.username.available ? 'text-green-600' : 'text-red-600'}`}>
                {validation.username.message}
              </p>
            )}
          </div>

          {/* 邮箱 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              邮箱 *
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="输入邮箱地址"
                disabled={loading}
                autoComplete="email"
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                {renderValidationIcon('email')}
              </div>
            </div>
            {validation.email.message && (
              <p className={`text-xs mt-1 ${validation.email.available ? 'text-green-600' : 'text-red-600'}`}>
                {validation.email.message}
              </p>
            )}
          </div>

          {/* 全名 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              姓名
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="输入姓名（可选）"
                disabled={loading}
                autoComplete="name"
              />
            </div>
          </div>

          {/* 密码 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              密码 *
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="输入密码（至少6位）"
                disabled={loading}
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                disabled={loading}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* 确认密码 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              确认密码 *
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="再次输入密码"
                disabled={loading}
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                disabled={loading}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* 注册按钮 */}
          <button
            type="submit"
            disabled={loading || validation.username.checking || validation.email.checking}
            className="w-full bg-gradient-to-r from-green-500 to-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:from-green-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader className="animate-spin h-5 w-5 mr-2" />
                注册中...
              </>
            ) : (
              <>
                <UserPlus className="h-5 w-5 mr-2" />
                立即注册
              </>
            )}
          </button>
        </form>

        {/* 底部链接 */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            已有账户？{' '}
            <Link
              to="/login"
              className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              立即登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;