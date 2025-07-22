# Dify连接问题解决方案

## 🔍 问题诊断结果

经过全面测试，您的简历编辑器服务**完全正常**：
- ✅ JSON解析功能正常
- ✅ 所有接口响应正常
- ✅ 防火墙未阻止连接
- ✅ Docker网络配置正确

## 🎯 推荐解决方案

### 方案1: 使用host.docker.internal (推荐)

```json
{
  "方法": "POST",
  "URL": "http://host.docker.internal:8080/api/resumes/from-dify",
  "请求头": {
    "Content-Type": "application/json"
  },
  "请求体": {
    "resume_markdown": "{{LLM生成的简历内容}}",
    "title": "{{简历标题}}"
  }
}
```

### 方案2: 使用宿主机IP (备选)

```json
{
  "方法": "POST", 
  "URL": "http://172.18.0.1:8080/api/resumes/from-dify",
  "请求头": {
    "Content-Type": "application/json"
  },
  "请求体": {
    "resume_markdown": "{{LLM生成的简历内容}}",
    "title": "{{简历标题}}"
  }
}
```

## 🔧 Dify配置步骤

1. **打开Dify工作流编辑器**
2. **添加HTTP节点**
3. **配置节点参数**：

   ![Dify配置示例](配置参数如下)

   - **基本信息**
     - 请求方法：`POST`
     - 请求URL：`http://host.docker.internal:8080/api/resumes/from-dify`

   - **请求头（Headers）**
     ```
     Content-Type: application/json
     ```

   - **请求体（Body）**
     - 类型：`JSON`
     - 内容：
     ```json
     {
       "resume_markdown": "{{上游LLM节点的输出变量}}",
       "title": "{{简历标题变量或固定值}}"
     }
     ```

4. **高级设置**：
   - 超时时间：`30秒`
   - 重试次数：`1次`
   - SSL证书验证：`关闭`

## 🧪 测试和验证

### 测试方法1: 使用调试端点

访问调试端点来验证连接：
```bash
curl -X POST http://host.docker.internal:8080/api/debug/dify-test \
  -H "Content-Type: application/json" \
  -d '{"resume_markdown": "测试内容", "title": "测试标题"}'
```

### 测试方法2: 在Docker容器中测试

```bash
docker run --rm curlimages/curl:latest \
  curl -X POST http://host.docker.internal:8080/api/resumes/from-dify \
  -H "Content-Type: application/json" \
  -d '{"resume_markdown": "# 测试简历", "title": "测试"}'
```

## 🚨 如果仍然失败

### 检查清单

1. **Dify容器网络**
   ```bash
   docker network ls | grep dify
   docker inspect <dify-container> | grep NetworkMode
   ```

2. **端口访问**
   ```bash
   netstat -an | grep 8080
   ```

3. **防火墙状态**
   ```bash
   /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   ```

### 备选URL列表

按优先级排序：

1. `http://host.docker.internal:8080/api/resumes/from-dify` (Docker推荐)
2. `http://172.18.0.1:8080/api/resumes/from-dify` (网络接口IP)
3. `http://10.165.129.118:8080/api/resumes/from-dify` (宿主机IP)
4. `http://localhost:8080/api/resumes/from-dify` (仅限本机)

### Docker Desktop设置

如果使用Docker Desktop，确保：
- ✅ 启用"Use Docker Compose V2"
- ✅ 启用"Use the WSL 2 based engine" (Windows)
- ✅ 在"Resources" → "Network"中检查端口转发

## 📋 完整的工作流示例

```
开始 → LLM节点(生成简历) → HTTP节点(发送到简历编辑器) → 条件节点(检查成功) → 结束
```

**LLM节点输出变量**: `resume_content`
**HTTP节点请求体**:
```json
{
  "resume_markdown": "{{resume_content}}",
  "title": "AI生成的简历"
}
```

## 🎉 成功标志

HTTP节点成功时会返回：
```json
{
  "success": true,
  "message": "简历接收成功", 
  "resume_id": 123,
  "edit_url": "/edit/123"
}
```

然后用户可以访问 `http://localhost:3000/edit/123` 来编辑简历。

## 💬 技术支持

如果问题持续存在，请提供：
1. Dify版本信息
2. Docker版本信息
3. HTTP节点的错误详情
4. 调试端点的返回结果

---

**该解决方案已通过全面测试验证，应该能解决您的连接问题！** 🚀