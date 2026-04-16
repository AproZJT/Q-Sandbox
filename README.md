# Q-Sandbox

这是一个偏轻量的本地练习项目，目标是“能跑、好改、别太复杂”。

## 现在保留的内容

- 前端：一个简单的代码输入和结果展示页
- 后端：一个最小可用的提交 + SSE 流式返回接口
- 沙箱：保留基本执行流程

## 已经精简掉的内容

- 复杂的 Milestone 流程说明
- 额外的管理、指标、认证相关入口
- Celery / Redis 相关配置
- 多余的调试页面和不必要的迁移脚本

## 本地启动

### 后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

## 说明

- 前端默认对接 `http://127.0.0.1:8000`
- 目前更适合个人练习和小型演示
- 如果后面还想继续瘦身，可以再把沙箱、SSE 续传、历史记录进一步简化
