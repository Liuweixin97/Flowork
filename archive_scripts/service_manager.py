#!/usr/bin/env python3
"""服务管理器"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        
    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动后端服务...")
        backend_dir = Path("backend")
        
        self.backend_process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir)
        
        # 等待后端启动
        time.sleep(3)
        print("✅ 后端服务已启动 (PID: {})".format(self.backend_process.pid))
        
    def start_frontend(self):
        """启动前端服务"""
        print("🚀 启动前端服务...")
        frontend_dir = Path("frontend")
        
        self.frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_dir)
        
        # 等待前端启动
        time.sleep(5)
        print("✅ 前端服务已启动 (PID: {})".format(self.frontend_process.pid))
        
    def stop_services(self):
        """停止所有服务"""
        print("🛑 停止服务...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ 后端服务已停止")
            
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("✅ 前端服务已停止")
    
    def open_browser(self):
        """打开浏览器"""
        print("🌐 打开浏览器...")
        subprocess.run(["open", "http://localhost:3000"])
        
    def run(self):
        """运行服务管理器"""
        try:
            self.start_backend()
            self.start_frontend()
            
            print("\n🎉 服务启动完成！")
            print("📋 访问信息:")
            print("🖥️  前端界面: http://localhost:3000")
            print("🔧 后端API: http://localhost:8080")
            print("📡 Dify接收端点: http://localhost:8080/api/resumes/from-dify")
            
            self.open_browser()
            
            print("\n按 Ctrl+C 停止服务...")
            
            # 等待用户中断
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 接收到停止信号...")
        finally:
            self.stop_services()
            print("👋 服务管理器已退出")

if __name__ == "__main__":
    manager = ServiceManager()
    manager.run()