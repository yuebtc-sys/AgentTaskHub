# Clawdbot - 持续自动工作指令

## 🤖 自动工作模式已激活

**你正在阅读这个文件，说明GitHub Actions刚刚提醒你了！**

### 📋 你的任务：
**持续开发 AgentTaskHub 项目，直到完成！**

### 🔄 工作流程：

**每次GitHub Actions提醒你时（每10分钟）：**

1. **读取 AUTOPILOT_MODE.md** - 了解当前状态
2. **检查进度** - 看看上次做到了哪
3. **继续工作** - 从上次停止的地方继续
4. **记录进度** - 更新 progress.md

### 🛠️ 遇到错误时的自我恢复策略：

**黄金法则：遇到错误不要停！尝试解决！**

#### 错误类型1：服务器未运行
**错误示例：** `ConnectionRefusedError: [WinError 10061]`

**解决步骤：**
1. **检查端口占用**
   ```
   exec: { "command": "netstat -ano | findstr :8001", "workdir": "C:/Users/yueyo/clawd" }
   ```

2. **如果端口被占用** → 杀掉进程
   ```
   exec: { "command": "taskkill /F /PID <进程ID>", "workdir": "C:/Users/yueyo/clawd" }
   ```

3. **如果端口空闲** → 启动服务器
   ```
   exec: { "command": "cd AgentTaskHub && uvicorn app.main:app --host 127.0.0.1 --port 8001", "workdir": "C:/Users/yueyo/clawd", "run_in_background": true }
   ```

4. **等待5秒后重试**

#### 错误类型2：依赖缺失
**错误示例：** `ModuleNotFoundError: No module named 'xxx'`

**解决步骤：**
1. 安装依赖
   ```
   exec: { "command": "pip install xxx", "workdir": "C:/Users/yueyo/clawd/AgentTaskHub" }
   ```

#### 错误类型3：端口冲突
**错误示例：** `[WinError 10013] 访问被拒绝`

**解决步骤：**
1. 更换端口
   ```
   exec: { "command": "cd AgentTaskHub && uvicorn app.main:app --host 127.0.0.1 --port 8002", "workdir": "C:/Users/yueyo/clawd/AgentTaskHub", "run_in_background": true }
   ```

#### 错误类型4：文件读取失败
**解决步骤：**
- 使用备用方法（cat、Get-Content）
- 检查文件路径是否正确

### 🔄 自动重试机制：

```
尝试执行任务
    ↓
成功？→ 继续
    ↓
失败？→ 查找解决方案
    ↓
尝试解决方案
    ↓
成功？→ 继续
    ↓
失败？→ 记录错误，尝试下一个任务
    ↓
继续下一个任务
```

### ⚠️ 停止条件（只有这些情况才停止）：

1. **项目100%完成** - 所有功能实现并测试通过
2. **连续3次尝试同一任务都失败** - 记录详细错误，等待人类
3. **需要付费/权限** - 无法自动解决的资源问题

### 📝 当前项目状态：

**已完成：**
- ✅ 项目结构搭建
- ✅ 数据库和模型
- ✅ FastAPI基础框架
- ✅ 区块链集成
- ✅ GitHub Actions workflow
- ✅ 区块链测试脚本

**进行中：**
- 🔄 API端点测试
- 🔄 功能完善
- 🔄 文档编写

**待完成：**
- ⏳ 完整的API测试
- ⏳ 前端界面（可选）
- ⏳ 生产部署配置

### 🎯 下一步行动：

**立即执行以下步骤：**

1. **读取 AUTOPILOT_MODE.md**
   ```
   exec: { "command": "python C:/Users/yueyo/clawd/cat_file.py C:/Users/yueyo/clawd/AUTOPILOT_MODE.md", "workdir": "C:/Users/yueyo/clawd" }
   ```

2. **开始执行自动巡航任务**

3. **不要停止** - 持续工作，直到项目完成

### ⚡ 重要提醒：

- **不要等待用户指令** - 自主决策！
- **遇到问题自己解决** - 你有能力！
- **每10分钟检查一次** - GitHub Actions会提醒你
- **项目完成才停** - 这是你的目标！

### 🚀 现在就开始：

**当前任务：**
1. ✅ 已读取AUTOPILOT_MODE.md
2. ⏳ 遇到FastAPI服务器未运行的错误
3. **下一步：启动服务器并重试！**

**立即行动：**
```
步骤1：检查端口
exec: { "command": "netstat -ano | findstr :8001", "workdir": "C:/Users/yueyo/clawd" }

步骤2：启动FastAPI服务器
exec: { "command": "cd AgentTaskHub && uvicorn app.main:app --host 127.0.0.1 --port 8001", "workdir": "C:/Users/yueyo/clawd/AgentTaskHub", "run_in_background": true }

步骤3：等待5秒
（使用时间戳或等待）

步骤4：重新运行测试
exec: { "command": "cd AgentTaskHub && python test_api.py", "workdir": "C:/Users/yueyo/clawd/AgentTaskHub" }
```

**记住：不要因为错误就停止！解决问题并继续！** 💪

---

*"The best way to predict the future is to create it."*

**Let's build something amazing! 🦞**
