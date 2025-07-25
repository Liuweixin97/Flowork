# 贡献指南

## 分支管理和发布流程

### 分支策略

我们采用简化的 Git Flow 策略：

#### 主要分支
- **master**: 生产稳定版本，只接受经过测试的功能合并
- **develop**: 开发主分支（预留，当前直接在master上开发）

#### 功能分支
- **feature/功能名称**: 新功能开发
- **hotfix/修复名称**: 紧急修复
- **release/版本号**: 版本发布准备

### 版本发布流程

#### 1. 功能开发
```bash
# 创建功能分支
git checkout -b feature/新功能名称

# 开发完成后合并到master
git checkout master
git merge feature/新功能名称 --no-ff
git branch -d feature/新功能名称
```

#### 2. 版本标记
```bash
# 创建版本标签
git tag -a v2.x.x -m "Release v2.x.x - 版本描述"

# 推送标签（如果需要）
git push origin v2.x.x
```

#### 3. 发布检查清单
- [ ] 所有功能分支已合并
- [ ] 测试通过
- [ ] 文档更新完成
- [ ] VERSION.md 更新
- [ ] CLAUDE.md 版本历史更新
- [ ] README.md 功能描述更新

### 提交消息规范

使用语义化提交信息：

```
类型(范围): 描述

feat: 新功能
fix: 修复
docs: 文档更新
style: 代码格式
refactor: 重构
perf: 性能优化
test: 测试相关
chore: 构建过程或辅助工具的变动
```

示例：
```bash
feat(auth): 添加用户认证系统
fix(pdf): 修复PDF导出字体问题
docs: 更新API文档
```

## 开发环境设置

### 必需工具
- Python 3.8+
- Node.js 16+
- Docker 20.10+
- Git 2.20+

### 本地开发
```bash
# 1. 克隆项目
git clone <repository-url>
cd 浩流简历编辑器

# 2. 安装依赖
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 3. 启动开发服务
./快速启动.sh
```

### 代码规范

#### Python 后端
- 使用 Black 格式化代码
- 遵循 PEP 8 规范
- 函数和类添加文档字符串

#### JavaScript 前端
- 使用 ESLint 检查代码
- 遵循 React 最佳实践
- 组件使用函数式写法

### 测试要求

- 新功能必须包含测试用例
- 修复必须包含回归测试
- 确保测试覆盖率不下降

## 贡献流程

### 1. 准备工作
```bash
# Fork 项目到你的账号
# 克隆你的 Fork
git clone https://github.com/your-username/resume-editor.git
cd resume-editor

# 添加上游仓库
git remote add upstream https://github.com/original/resume-editor.git
```

### 2. 开发新功能
```bash
# 同步上游更改
git fetch upstream
git checkout master
git merge upstream/master

# 创建功能分支
git checkout -b feature/amazing-feature

# 进行开发...
# 提交更改
git commit -m "feat: 添加了惊人的新功能"
```

### 3. 提交 Pull Request
1. 将更改推送到你的 Fork
2. 在 GitHub 上创建 Pull Request
3. 详细描述你的更改
4. 等待代码审查

### Pull Request 模板
```markdown
## 更改描述
简要描述本次更改的内容和目的

## 更改类型
- [ ] 新功能
- [ ] 修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他

## 测试
- [ ] 已在本地测试
- [ ] 包含单元测试
- [ ] 包含集成测试

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 更新了相关文档
- [ ] 自测通过
```

## 版本管理

### 语义化版本控制
我们遵循 [Semantic Versioning](https://semver.org/):

- **主版本号(MAJOR)**: 不兼容的API修改
- **次版本号(MINOR)**: 向下兼容的功能性新增
- **修订号(PATCH)**: 向下兼容的问题修正

### 发布周期
- **主版本**: 重大架构变更或不兼容更新
- **次版本**: 每月发布，包含新功能
- **修订版**: 根据需要发布，修复关键问题

## 社区

### 获取帮助
- 查阅 [CLAUDE.md](./CLAUDE.md) 获取详细文档
- 提交 Issue 报告问题
- 参与 Discussions 讨论

### 行为准则
- 尊重所有参与者
- 建设性地讨论问题
- 欢迎新手贡献者
- 专注于技术问题

---

感谢你对浩流简历编辑器项目的贡献！🎉