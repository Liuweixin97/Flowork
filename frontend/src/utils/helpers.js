/**
 * 格式化日期
 */
export const formatDate = (dateString) => {
  if (!dateString) return '';
  
  // 确保正确处理UTC时间戳
  let date;
  if (dateString.endsWith('Z') || dateString.includes('+')) {
    // 已经是ISO格式，直接解析
    date = new Date(dateString);
  } else {
    // 假设是UTC时间，添加Z后缀
    date = new Date(dateString + (dateString.includes('T') ? 'Z' : 'T00:00:00Z'));
  }
  
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Shanghai'
  }).format(date);
};

/**
 * 格式化相对时间
 */
export const formatRelativeTime = (dateString) => {
  if (!dateString) return '';
  
  // 确保正确处理UTC时间戳
  let date;
  if (dateString.endsWith('Z') || dateString.includes('+')) {
    // 已经是ISO格式，直接解析
    date = new Date(dateString);
  } else {
    // 假设是UTC时间，添加Z后缀
    date = new Date(dateString + (dateString.includes('T') ? 'Z' : 'T00:00:00Z'));
  }
  
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) {
    return '刚刚';
  } else if (diffInSeconds < 3600) {
    return `${Math.floor(diffInSeconds / 60)}分钟前`;
  } else if (diffInSeconds < 86400) {
    return `${Math.floor(diffInSeconds / 3600)}小时前`;
  } else if (diffInSeconds < 2592000) {
    return `${Math.floor(diffInSeconds / 86400)}天前`;
  } else {
    return formatDate(dateString);
  }
};

/**
 * 下载文件
 */
export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * 复制文本到剪贴板
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // 降级方案
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      return true;
    } catch (err) {
      return false;
    } finally {
      document.body.removeChild(textArea);
    }
  }
};

/**
 * 节流函数
 */
export const throttle = (func, delay) => {
  let timeoutId;
  let lastExecTime = 0;
  return function (...args) {
    const currentTime = Date.now();
    
    if (currentTime - lastExecTime > delay) {
      func.apply(this, args);
      lastExecTime = currentTime;
    } else {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        func.apply(this, args);
        lastExecTime = Date.now();
      }, delay - (currentTime - lastExecTime));
    }
  };
};

/**
 * 防抖函数
 */
export const debounce = (func, delay) => {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
};

/**
 * 检查字符串是否为空
 */
export const isEmpty = (str) => {
  return !str || str.trim().length === 0;
};

/**
 * 截取字符串
 */
export const truncate = (str, maxLength = 100) => {
  if (!str) return '';
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength) + '...';
};

/**
 * 生成随机ID
 */
export const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * 清理Markdown符号
 */
export const cleanMarkdown = (text) => {
  if (!text) return '';
  
  let cleaned = text;
  
  // 移除标题标记 (#)
  cleaned = cleaned.replace(/^#+\s*/gm, '');
  
  // 移除粗体标记 (**)
  cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, '$1');
  
  // 移除斜体标记 (*)
  cleaned = cleaned.replace(/\*(.*?)\*/g, '$1');
  
  // 移除代码标记 (`)
  cleaned = cleaned.replace(/`(.*?)`/g, '$1');
  
  // 移除链接标记 [text](url)
  cleaned = cleaned.replace(/\[(.*?)\]\(.*?\)/g, '$1');
  
  // 移除下划线标记 (_)
  cleaned = cleaned.replace(/_(.*?)_/g, '$1');
  
  // 移除列表标记
  cleaned = cleaned.replace(/^\s*[-*+]\s+/gm, '');
  
  // 移除数字列表标记
  cleaned = cleaned.replace(/^\s*\d+\.\s+/gm, '');
  
  // 移除水平分隔线
  cleaned = cleaned.replace(/^---+$/gm, '');
  
  // 移除块引用标记
  cleaned = cleaned.replace(/^>\s*/gm, '');
  
  // 清理多余的空行
  cleaned = cleaned.replace(/\n\s*\n\s*\n/g, '\n\n');
  
  // 移除行首行尾空白
  cleaned = cleaned.trim();
  
  return cleaned;
};