import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ResumesPage from './pages/ResumesPage';
import EditPage from './pages/EditPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <Routes>
            {/* 认证页面不需要Layout包装 */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* 主应用页面使用Layout */}
            <Route path="/*" element={
              <Layout>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/resumes" element={<ResumesPage />} />
                  <Route path="/edit/:id" element={<EditPage />} />
                </Routes>
              </Layout>
            } />
          </Routes>
          
          {/* Toast通知 - 调整位置避免遮住用户菜单 */}
          <Toaster
            position="top-center"
            gutter={8}
            containerStyle={{
              top: 80, // 导航栏下方
            }}
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
                maxWidth: '500px',
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
      </AuthProvider>
    </Router>
  );
}

export default App;