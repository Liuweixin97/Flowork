## 开发需求文档

### 基本要求

- 始终以中文输出提示/步骤
- 注意版本管理，新版本需要在 Git 提交版本，以方便回滚（/Users/liuweixin/Desktop/MyProjects/浩流简历编辑器/.git ）
- 更新日志、技术框架等信息以中文补充在 Claude.md 文件（/Users/liuweixin/Desktop/MyProjects/浩流简历编辑器/CLAUDE.md ）
- 每次开发完成后，都要启动好前后端服务给我测试

### 基本信息

- 编辑器（浩流简历）位于（/Users/liuweixin/Desktop/MyProjects/浩流简 历编辑器）

- Dify 位于（/Users/liuweixin/Desktop/MyProjects/dify ）

- 该项目与 Dify 集成，参考 API 使用文档（/Users/liuweixin/Desktop/MyProjects/浩流简历编辑器/工作流编排对话型应用\ API.md ）

- Dify 的项目文件夹位于（/Users/liuweixin/Desktop/MyProjects/dify ），你通常不应该修改 Dify

- 该项目将在本机使用贝锐花生壳进行**内网穿透**

  > 简历后端API
  >
  > 访问地址：http://mi3qm328989.vicp.fun:45093/
  >
  > 内网主机：127.0.0.1:8080
  >
  > 简历编辑器
  >
  > 访问地址：http://mi3qm328989.vicp.fun/
  >
  > 内网主机：127.0.0.1:3000

### 开发需求

- 启动编辑器前后端服务、Dify、内网穿透
