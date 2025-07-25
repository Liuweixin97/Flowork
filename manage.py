#!/usr/bin/env python3
"""
简历编辑器统一服务管理器
支持本地开发和Docker部署模式，集成内网穿透配置
"""

import os
import sys
import subprocess
import time
import signal
import json
import urllib.request
from pathlib import Path
import argparse

class ServiceManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
        self.dify_dir = Path("/Users/liuweixin/Desktop/MyProjects/dify")
        
        # 进程记录
        self.pids = {}
        self.pid_files = {
            'backend': self.base_dir / "backend.pid",
            'frontend': self.base_dir / "frontend.pid",
            'mock_dify': self.base_dir / "mock_dify.pid"
        }
        
        # 服务端口配置
        self.ports = {
            'backend': 8080,
            'frontend': 3000,
            'mock_dify': 8001,
            'dify': 80
        }
        
        # 内网穿透配置
        self.tunnel_config = {
            'backend_url': 'http://mi3qm328989.vicp.fun:45093',
            'frontend_url': 'http://mi3qm328989.vicp.fun'
        }
    
    def print_status(self, message, status='info'):
        """打印状态信息"""
        colors = {
            'info': '\033[0;34m',     # 蓝色
            'success': '\033[0;32m',  # 绿色
            'warning': '\033[1;33m',  # 黄色
            'error': '\033[0;31m',    # 红色
            'reset': '\033[0m'        # 重置颜色
        }
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        color = colors.get(status, colors['info'])
        icon = icons.get(status, 'ℹ️')
        
        print(f"{color}{icon} {message}{colors['reset']}")
    
    def check_dependencies(self):
        """检查系统依赖"""
        self.print_status("检查系统依赖...")
        
        deps = [
            ('python3', 'Python 3'),
            ('npm', 'Node.js/npm'),
            ('docker', 'Docker (可选)'),
            ('docker-compose', 'Docker Compose (可选)')
        ]
        
        missing = []
        for cmd, name in deps:
            if not self._command_exists(cmd):
                if cmd in ['docker', 'docker-compose']:
                    self.print_status(f"{name} 未安装 (Docker模式需要)", 'warning')
                else:
                    missing.append(name)
        
        if missing:
            self.print_status(f"缺少必要依赖: {', '.join(missing)}", 'error')
            return False
        
        self.print_status("系统依赖检查通过", 'success')
        return True
    
    def _command_exists(self, command):
        """检查命令是否存在"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def check_port(self, port):
        """检查端口是否被占用"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                    capture_output=True, text=True)
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def kill_port(self, port):
        """终止占用指定端口的进程"""
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                    capture_output=True, text=True)
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
                    self.print_status(f"终止端口 {port} 上的进程 (PID: {pid})")
        except Exception as e:
            self.print_status(f"清理端口 {port} 失败: {e}", 'warning')
    
    def cleanup_ports(self):
        """清理所有服务端口"""
        self.print_status("清理端口占用...")
        for service, port in self.ports.items():
            if self.check_port(port):
                self.kill_port(port)
    
    def save_pid(self, service, pid):
        """保存进程ID"""
        self.pids[service] = pid
        self.pid_files[service].write_text(str(pid))
    
    def load_pid(self, service):
        """加载进程ID"""
        pid_file = self.pid_files.get(service)
        if pid_file and pid_file.exists():
            try:
                return int(pid_file.read_text().strip())
            except:
                pass
        return None
    
    def is_process_running(self, pid):
        """检查进程是否运行"""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, TypeError):
            return False
    
    def start_backend(self):
        """启动后端服务"""
        self.print_status("启动后端服务...")
        
        # 检查虚拟环境
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            self.print_status("创建Python虚拟环境...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                          cwd=self.backend_dir, check=True)
        
        # 安装依赖
        pip_path = venv_path / "bin" / "pip"
        if pip_path.exists():
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], 
                          cwd=self.backend_dir, capture_output=True)
        else:
            # 使用激活虚拟环境的方式安装依赖
            activate_script = venv_path / "bin" / "activate"
            install_cmd = f"source {activate_script} && pip install -r requirements.txt"
            subprocess.run(install_cmd, shell=True, cwd=self.backend_dir)
        
        # 启动服务
        python_path = venv_path / "bin" / "python"
        process = subprocess.Popen([str(python_path), "app.py"], 
                                  cwd=self.backend_dir)
        
        self.save_pid('backend', process.pid)
        time.sleep(3)
        
        # 验证启动
        if self.is_process_running(process.pid):
            self.print_status(f"后端服务已启动 (PID: {process.pid})", 'success')
            return True
        else:
            self.print_status("后端服务启动失败", 'error')
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        self.print_status("启动前端服务...")
        
        # 检查依赖
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            self.print_status("安装前端依赖...")
            subprocess.run(["npm", "install"], cwd=self.frontend_dir)
        
        # 启动服务
        process = subprocess.Popen(["npm", "run", "dev"], 
                                  cwd=self.frontend_dir)
        
        self.save_pid('frontend', process.pid)
        time.sleep(5)
        
        # 验证启动
        if self.is_process_running(process.pid):
            self.print_status(f"前端服务已启动 (PID: {process.pid})", 'success')
            return True
        else:
            self.print_status("前端服务启动失败", 'error')
            return False
    
    def start_mock_dify(self):
        """启动模拟Dify服务"""
        mock_dify_file = self.base_dir / "mock_dify_service.py"
        if not mock_dify_file.exists():
            self.print_status("模拟Dify服务文件不存在，跳过", 'warning')
            return True
        
        self.print_status("启动模拟Dify服务...")
        process = subprocess.Popen([sys.executable, str(mock_dify_file)])
        
        self.save_pid('mock_dify', process.pid)
        time.sleep(2)
        
        if self.is_process_running(process.pid):
            self.print_status(f"模拟Dify服务已启动 (PID: {process.pid})", 'success')
            return True
        else:
            self.print_status("模拟Dify服务启动失败", 'error')
            return False
    
    def start_dify(self):
        """启动Dify服务"""
        if not self.dify_dir.exists():
            self.print_status("Dify目录不存在，跳过启动Dify", 'warning')
            return False
        
        self.print_status("启动Dify服务...")
        try:
            subprocess.run(["docker-compose", "up", "-d"], 
                          cwd=self.dify_dir, check=True)
            self.print_status("Dify服务已启动", 'success')
            return True
        except subprocess.CalledProcessError:
            self.print_status("Dify服务启动失败", 'error')
            return False
    
    def stop_service(self, service):
        """停止指定服务"""
        pid = self.load_pid(service)
        if pid and self.is_process_running(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                if self.is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
                self.print_status(f"{service}服务已停止")
            except OSError:
                pass
        
        # 清理PID文件
        pid_file = self.pid_files.get(service)
        if pid_file and pid_file.exists():
            pid_file.unlink()
    
    def stop_all(self):
        """停止所有服务"""
        self.print_status("停止所有服务...")
        
        for service in self.pid_files.keys():
            self.stop_service(service)
        
        # 清理端口
        self.cleanup_ports()
        
        self.print_status("所有服务已停止", 'success')
    
    def check_health(self):
        """检查服务健康状态"""
        self.print_status("检查服务健康状态...")
        
        services_status = {}
        
        # 检查后端
        try:
            response = urllib.request.urlopen("http://localhost:8080/api/health", timeout=5)
            if response.getcode() == 200:
                services_status['backend'] = 'healthy'
                self.print_status("后端服务运行正常", 'success')
            else:
                services_status['backend'] = 'unhealthy'
                self.print_status("后端服务响应异常", 'error')
        except Exception:
            services_status['backend'] = 'down'
            self.print_status("后端服务连接失败", 'error')
        
        # 检查前端
        try:
            response = urllib.request.urlopen("http://localhost:3000", timeout=5)
            if response.getcode() == 200:
                services_status['frontend'] = 'healthy'
                self.print_status("前端服务运行正常", 'success')
            else:
                services_status['frontend'] = 'unhealthy'
                self.print_status("前端服务响应异常", 'error')
        except Exception:
            # 尝试3001端口
            try:
                response = urllib.request.urlopen("http://localhost:3001", timeout=5)
                if response.getcode() == 200:
                    services_status['frontend'] = 'healthy'
                    self.print_status("前端服务运行正常 (端口3001)", 'success')
                else:
                    services_status['frontend'] = 'unhealthy'
            except Exception:
                services_status['frontend'] = 'down'
                self.print_status("前端服务连接失败", 'error')
        
        return services_status
    
    def start_local(self):
        """启动本地开发环境"""
        self.print_status("启动本地开发环境...")
        
        if not self.check_dependencies():
            return False
        
        # 清理端口
        self.cleanup_ports()
        
        # 启动服务
        success = True
        success &= self.start_backend()
        success &= self.start_frontend()
        
        if success:
            self.print_status("本地开发环境启动成功！", 'success')
            self.show_info()
            return True
        else:
            self.print_status("启动过程中遇到错误", 'error')
            return False
    
    def start_docker(self):
        """使用Docker启动服务"""
        self.print_status("使用Docker启动服务...")
        
        try:
            subprocess.run(["docker-compose", "up", "--build", "-d"], 
                          cwd=self.base_dir, check=True)
            time.sleep(10)
            self.print_status("Docker服务启动成功！", 'success')
            self.show_info()
            return True
        except subprocess.CalledProcessError:
            self.print_status("Docker服务启动失败", 'error')
            return False
    
    def show_info(self):
        """显示服务信息"""
        print("\n" + "="*50)
        print("🎉 浩流简历编辑器服务信息")
        print("="*50)
        print(f"📱 前端界面: http://localhost:3000")
        print(f"🔧 后端API: http://localhost:8080")
        print(f"📡 Dify接收端点: http://localhost:8080/api/resumes/from-dify")
        print("\n🌐 内网穿透地址:")
        print(f"   前端: {self.tunnel_config['frontend_url']}")
        print(f"   后端: {self.tunnel_config['backend_url']}")
        print("\n📋 管理命令:")
        print("   查看状态: python3 manage.py status")
        print("   停止服务: python3 manage.py stop")
        print("   重启服务: python3 manage.py restart")
        print("="*50)

def main():
    parser = argparse.ArgumentParser(description='浩流简历编辑器服务管理器')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'docker', 'dify'], 
                       help='执行的操作')
    parser.add_argument('--cleanup', action='store_true', help='清理端口占用')
    
    args = parser.parse_args()
    manager = ServiceManager()
    
    try:
        if args.action == 'start':
            manager.start_local()
        elif args.action == 'docker':
            manager.start_docker()
        elif args.action == 'stop':
            manager.stop_all()
        elif args.action == 'restart':
            manager.stop_all()
            time.sleep(2)
            manager.start_local()
        elif args.action == 'status':
            manager.check_health()
        elif args.action == 'dify':
            manager.start_dify()
        elif args.cleanup:
            manager.cleanup_ports()
            
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止服务...")
        manager.stop_all()
    except Exception as e:
        manager.print_status(f"执行出错: {e}", 'error')
        sys.exit(1)

if __name__ == "__main__":
    main()