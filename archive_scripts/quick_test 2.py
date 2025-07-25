#!/usr/bin/env python3
"""快速测试脚本"""

import sys
import subprocess
import time
import requests
from pathlib import Path

def test_basic():
    print("🧪 开始基础测试...")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 创建.env文件
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("📝 创建.env配置文件...")
        with open(env_file, "w") as f:
            f.write("FLASK_DEBUG=True\nSECRET_KEY=test\nHOST=0.0.0.0\nPORT=8080\n")
    
    # 检查基本导入
    try:
        import flask
        print("✅ Flask可用")
    except ImportError:
        print("❌ Flask未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Flask", "Flask-SQLAlchemy", "Flask-CORS", "python-markdown", "python-dotenv"], check=True)
        print("✅ 依赖安装完成")
    
    print("🎉 基础测试完成！")

if __name__ == "__main__":
    test_basic()