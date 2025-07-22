import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import EditPage from './pages/EditPage';
import { useNotifications } from './hooks/useNotifications';

// 内部App组件，使用通知hook
function AppContent() {
  // 启用实时通知监听
  const { isConnected, lastEvent } = useNotifications(true);
  
  return (
    <div className="App">
      {/* 调试信息 - 开发环境下显示连接状态 */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed top-0 right-0 z-50 bg-black bg-opacity-75 text-white text-xs p-2 m-2 rounded">
          <div>SSE: {isConnected ? '🟢 已连接' : '🔴 断开'}</div>
          {lastEvent && (
            <div>最后事件: {lastEvent.type}</div>
          )}
        </div>
      )}
      
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/edit/:id" element={<EditPage />} />
        </Routes>
      </Layout>
      
      {/* Toast通知 */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            style: {
              background: '#10b981',
            },
          },
          error: {
            duration: 5000,
            style: {
              background: '#ef4444',
            },
          },
        }}
      />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;