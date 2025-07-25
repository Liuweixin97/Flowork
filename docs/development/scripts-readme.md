# 浩流简历编辑器 - 服务管理脚本说明

## 快速使用

### 中文脚本（推荐）
```bash
# 快速启动本地开发环境
./快速启动.sh

# 停止所有服务
./快速停止.sh

# 启动完整环境（包括Dify）
./启动完整环境.sh

# 检查服务状态
./检查状态.sh
```

### 统一管理脚本
```bash
# 启动本地开发环境
python3 manage.py start

# 使用Docker启动
python3 manage.py docker

# 停止所有服务
python3 manage.py stop

# 重启服务
python3 manage.py restart

# 检查服务状态
python3 manage.py status

# 启动Dify
python3 manage.py dify

# 清理端口占用
python3 manage.py --cleanup
```

## 服务信息

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8080  
- **Dify接收端点**: http://localhost:8080/api/resumes/from-dify

### 内网穿透地址
- **前端**: http://mi3qm328989.vicp.fun
- **后端**: http://mi3qm328989.vicp.fun:45093

## 故障排除

1. **端口被占用**: 运行 `python3 manage.py --cleanup` 清理端口
2. **服务启动失败**: 检查 `backend.log` 和 `frontend.log` 日志文件
3. **依赖问题**: 确保已安装 Python 3 和 Node.js

## 旧脚本归档

旧的脚本文件已移动到 `archive_scripts/` 文件夹中，如有需要可以查看。