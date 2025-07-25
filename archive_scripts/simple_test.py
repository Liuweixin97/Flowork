#!/usr/bin/env python3
"""简单测试脚本"""

import sys
import subprocess
from pathlib import Path

def main():
    print("🧪 简历编辑器 - 简单测试")
    print(f"Python版本: {sys.version}")
    
    # 检查项目结构
    print("\n📁 检查项目结构...")
    backend_dir = Path("backend")
    frontend_dir = Path("frontend")
    
    if backend_dir.exists():
        print("✅ backend目录存在")
        
        # 检查关键文件
        if (backend_dir / "app.py").exists():
            print("✅ app.py存在")
        if (backend_dir / "requirements.txt").exists():
            print("✅ requirements.txt存在")
        if (backend_dir / "models.py").exists():
            print("✅ models.py存在")
            
    if frontend_dir.exists():
        print("✅ frontend目录存在")
        
        if (frontend_dir / "package.json").exists():
            print("✅ package.json存在")
        if (frontend_dir / "src").exists():
            print("✅ src目录存在")
    
    # 创建.env文件
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("\n📝 创建.env配置文件...")
        with open(env_file, "w") as f:
            f.write("""FLASK_DEBUG=True
SECRET_KEY=test-secret-key-change-in-production
HOST=0.0.0.0
PORT=8080
DATABASE_URL=sqlite:///resume_editor.db
""")
        print("✅ .env文件创建成功")
    
    # 创建前端.env文件
    frontend_env = frontend_dir / ".env"
    if not frontend_env.exists():
        print("📝 创建前端.env配置文件...")
        with open(frontend_env, "w") as f:
            f.write("VITE_API_URL=http://localhost:8080\n")
        print("✅ 前端.env文件创建成功")
    
    print("\n🎉 基础检查完成！")
    print("\n📋 下一步操作:")
    print("1. 安装后端依赖: cd backend && pip install -r requirements.txt")
    print("2. 启动后端服务: cd backend && python app.py")
    print("3. 安装前端依赖: cd frontend && npm install")
    print("4. 启动前端服务: cd frontend && npm run dev")
    print("5. 或者使用Docker: ./start.sh")

if __name__ == "__main__":
    main()