import React, { useState, useEffect, useRef } from 'react';
import { X, Send, MessageCircle, User, Bot, Loader2, CheckCircle, AlertCircle, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { chatflowAPI } from '../utils/api';
import toast from 'react-hot-toast';

const ChatflowDialog = ({ isOpen, onClose, onResumeGenerated }) => {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStatus, setConversationStatus] = useState('inactive'); // inactive, starting, active, completed, error
  const [generatedResume, setGeneratedResume] = useState(null);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // 自动滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // 重置对话状态
  useEffect(() => {
    if (!isOpen) {
      // 对话框关闭时清理状态
      setMessages([]);
      setInputMessage('');
      setConversationId(null);
      setConversationStatus('inactive');
      setGeneratedResume(null);
    }
  }, [isOpen]);
  
  // 启动对话
  const startConversation = async () => {
    try {
      setIsLoading(true);
      setConversationStatus('starting');
      
      const response = await chatflowAPI.startConversation();
      
      if (response.data.success) {
        const { conversation_id, initial_message } = response.data;
        setConversationId(conversation_id);
        setConversationStatus('active');
        
        // 添加初始消息
        const initialMsg = {
          id: Date.now(),
          type: 'assistant',
          content: initial_message,
          timestamp: new Date()
        };
        
        setMessages([initialMsg]);
        toast.success('浩流简历·flowork已启动');
        
        // 聚焦输入框
        setTimeout(() => inputRef.current?.focus(), 100);
      } else {
        throw new Error(response.data.error || '启动对话失败');
      }
    } catch (error) {
      console.error('启动对话失败:', error);
      setConversationStatus('error');
      toast.error('启动浩流简历·flowork失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };
  
  // 发送消息 - 使用流式API
  const sendMessage = async () => {
    if (!inputMessage.trim() || !conversationId || isLoading) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    
    // 创建流式助手消息
    const streamingMessageId = Date.now() + 1;
    const streamingMessage = {
      id: streamingMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      suggestions: [],
      isStreaming: true
    };
    
    setMessages(prev => [...prev, streamingMessage]);
    
    try {
      await chatflowAPI.sendStreamMessage(
        conversationId, 
        currentMessage,
        {},
        // onChunk: 处理流式内容块
        (chunk) => {
          setMessages(prev => prev.map(msg => 
            msg.id === streamingMessageId 
              ? { ...msg, content: msg.content + chunk }
              : msg
          ));
        },
        // onComplete: 处理完成事件
        (data) => {
          setMessages(prev => prev.map(msg => 
            msg.id === streamingMessageId 
              ? { ...msg, isStreaming: false }
              : msg
          ));
          
          // 检查是否完成简历生成
          if (data.status === 'completed' && data.resume_content) {
            setConversationStatus('completed');
            setGeneratedResume({
              content: data.resume_content,
              resumeId: data.resume_id,
              editUrl: data.edit_url
            });
            
            toast.success('简历生成完成！');
          }
          
          setIsLoading(false);
        },
        // onError: 处理错误
        (error) => {
          console.error('流式消息发送失败:', error);
          
          // 移除流式消息并添加错误消息
          setMessages(prev => prev.filter(msg => msg.id !== streamingMessageId));
          
          const errorMessage = {
            id: Date.now() + 2,
            type: 'system',
            content: '抱歉，消息发送失败，请重试。',
            timestamp: new Date(),
            isError: true
          };
          
          setMessages(prev => [...prev, errorMessage]);
          toast.error('消息发送失败');
          setIsLoading(false);
        }
      );
    } catch (error) {
      console.error('发送流式消息失败:', error);
      
      // 移除流式消息并添加错误消息
      setMessages(prev => prev.filter(msg => msg.id !== streamingMessageId));
      
      const errorMessage = {
        id: Date.now() + 2,
        type: 'system',
        content: '抱歉，消息发送失败，请重试。',
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
      toast.error('消息发送失败');
      setIsLoading(false);
    }
  };
  
  // 处理Enter键发送
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  // 使用生成的简历
  const useGeneratedResume = () => {
    if (generatedResume && onResumeGenerated) {
      onResumeGenerated(generatedResume);
      onClose();
    }
  };
  
  // 关闭对话并清理
  const handleClose = async () => {
    if (conversationId && conversationStatus === 'active') {
      try {
        await chatflowAPI.endConversation(conversationId);
      } catch (error) {
        console.error('结束对话失败:', error);
      }
    }
    onClose();
  };
  
  // 检测消息是否包含 Markdown 格式
  const hasMarkdown = (content) => {
    return content && (
      content.includes('# ') || 
      content.includes('## ') ||
      content.includes('### ') ||
      content.includes('- ') ||
      content.includes('* ') ||
      content.includes('**') ||
      content.includes('`') ||
      content.includes('[') ||
      content.includes('\n\n')
    );
  };

  // 检测消息是否包含简历内容
  const hasResumeContent = (content) => {
    return content && (
      content.includes('# ') && (
        content.includes('个人信息') ||
        content.includes('工作经历') ||
        content.includes('教育背景') ||
        content.includes('技能') ||
        content.includes('项目经验')
      )
    );
  };

  // 复制内容到剪贴板
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  
  const copyToClipboard = async (content, messageId) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      toast.success('已复制到剪贴板');
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (error) {
      toast.error('复制失败');
    }
  };

  // 自定义 Markdown 组件样式（使用统一的 CSS 类）
  const MarkdownComponents = {
    // 为链接添加安全属性
    a: ({children, href}) => (
      <a href={href} className="text-blue-600 hover:text-blue-800 hover:underline" target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    ),
  };

  // 消息组件
  const MessageBubble = ({ message }) => {
    const isUser = message.type === 'user';
    const isSystem = message.type === 'system';
    const shouldRenderMarkdown = !isUser && hasMarkdown(message.content);
    
    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex items-start space-x-2 max-w-[85%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : isSystem 
                ? 'bg-gray-400 text-white'
                : 'bg-green-500 text-white'
          }`}>
            {isUser ? <User className="h-4 w-4" /> : isSystem ? <AlertCircle className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
          </div>
          
          <div className={`rounded-lg px-4 py-3 ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : isSystem && message.isError
                ? 'bg-red-100 text-red-800 border border-red-200'
                : 'bg-gray-100 text-gray-800'
          }`}>
            {shouldRenderMarkdown ? (
              <div className="markdown-content relative">
                <ReactMarkdown components={MarkdownComponents}>
                  {message.content}
                </ReactMarkdown>
                {/* 如果是简历内容，显示复制按钮 */}
                {hasResumeContent(message.content) && (
                  <button
                    onClick={() => copyToClipboard(message.content, message.id)}
                    className="absolute top-2 right-2 p-1.5 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors shadow-sm"
                    title="复制简历内容"
                  >
                    {copiedMessageId === message.id ? (
                      <Check className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-500" />
                    )}
                  </button>
                )}
              </div>
            ) : (
              <div className="whitespace-pre-wrap">{message.content}</div>
            )}
            
            {/* 显示建议选项 */}
            {message.suggestions && message.suggestions.length > 0 && (
              <div className="mt-2 space-y-1">
                {message.suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="block w-full text-left px-2 py-1 text-sm bg-white bg-opacity-20 rounded hover:bg-opacity-30 transition-colors"
                    onClick={() => {
                      setInputMessage(suggestion);
                      inputRef.current?.focus();
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
            
            <div className="text-xs mt-1 opacity-70">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-2xl h-[600px] flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <MessageCircle className="h-5 w-5 text-green-500" />
            <h3 className="text-lg font-semibold">浩流简历·flowork</h3>
            <span className={`px-2 py-1 text-xs rounded-full ${
              conversationStatus === 'active' 
                ? 'bg-green-100 text-green-800' 
                : conversationStatus === 'completed'
                  ? 'bg-blue-100 text-blue-800'
                  : conversationStatus === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
            }`}>
              {conversationStatus === 'active' && '对话中'}
              {conversationStatus === 'starting' && '启动中'}
              {conversationStatus === 'completed' && '已完成'}
              {conversationStatus === 'error' && '错误'}
              {conversationStatus === 'inactive' && '未启动'}
            </span>
          </div>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {conversationStatus === 'inactive' && (
            <div className="text-center py-12">
              <Bot className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h4 className="text-lg font-medium text-gray-700 mb-2">浩流简历·flowork</h4>
              <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                我是浩流简历·flowork智能助手，将引导您一步步创建个人简历，包括基本信息、工作经历、教育背景、技能专长等内容。
              </p>
              <button
                onClick={startConversation}
                disabled={isLoading}
                className="btn-primary flex items-center space-x-2 mx-auto"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <MessageCircle className="h-4 w-4" />
                )}
                <span>{isLoading ? '启动中...' : '开始创建简历'}</span>
              </button>
            </div>
          )}
          
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg px-4 py-2">
                <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                <span className="text-gray-600">浩流简历·flowork正在思考...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* 完成状态显示 */}
        {conversationStatus === 'completed' && generatedResume && (
          <div className="px-4 py-3 bg-green-50 border-t border-green-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-green-800 font-medium">简历生成完成</span>
              </div>
              <button
                onClick={useGeneratedResume}
                className="btn-primary text-sm"
              >
                使用这份简历
              </button>
            </div>
          </div>
        )}
        
        {/* 输入区域 */}
        {conversationStatus === 'active' && (
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入您的回答..."
                disabled={isLoading}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="btn-primary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                <span>发送</span>
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              按 Enter 发送消息，Shift + Enter 换行
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatflowDialog;