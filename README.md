# API 通知网关系统 (Notification Gateway MVP)

## 1. 项目概述
本项目是一个基于事件驱动架构的 API 通知网关（Outbound Webhook Gateway）。旨在解耦内部业务系统与外部供应商 API，提供高可靠、可配置的异步通知投递服务。

## 2. 系统核心设计
### 2.1 架构组件
*   **Web Server**: FastAPI, 接收业务请求，进行基础校验并入队。
*   **Queue**: Redis + Python RQ, 实现异步处理与削峰填谷。
*   **Worker**: 无状态消费者，负责模板渲染、HTTP 请求发送与重试逻辑。
*   **Template**: Jinja2, 用于灵活适配异构的 Vendor API 格式。

### 2.2 关键工程决策
*   **Redis Queue over Kafka/Celery**: 考虑到 MVP 的时间限制（4小时）与部署轻量化需求，选择了 Redis Queue。它部署简单（无 Zookeper 依赖），且足以支撑 MVP 阶段的吞吐量。
*   **At-Least-Once 投递语义**: 为了保证核心业务“不丢单”，系统发生网络超时或 5xx 错误时会进行重试，意味着外部可能收到重复请求。通过 `idempotency_key` 支持幂等性。
*   **指数退避与抖动 (Exponential Backoff with Jitter)**: 避免重试风暴（Thundering Herd）。使用 `tenacity` 库实现 `wait_exponential_jitter`，确保重试流量均匀分布。
*   **配置化适配**: 使用 Jinja2 模板将 Vendor 的异构 API（Header/Body）差异通过配置抹平，无需修改代码即可接入新供应商。

### 2.3 系统边界
*   **In-Scope**: 请求缓冲、协议转换、自动重试、死信处理。
*   **Out-of-Scope**: 复杂的 OAuth2 flow（假设长效 Token）、入站 Webhook 处理、业务逻辑校验。

## 3. 目录结构
```bash
rc_project/
├── app/
│   ├── main.py           # API 入口
│   ├── tasks.py          # 核心任务逻辑
│   ├── worker.py         # Worker 启动脚本
│   ├── config.py         # 配置项
│   └── services/         # 服务层
├── docker-compose.yml    # 容器编排
├── Dockerfile            # 镜像构建
└── requirements.txt      # 依赖管理
```

## 4. AI 使用说明
本项目在 AI (Google Gemini, OpenAI GPT-4) 的辅助下完成：
*   **算法选择**: 采纳了 AI 建议的 `Decorrelated Jitter` 算法用于重试策略。
*   **模板选型**: 采纳了 AI 推荐的 `Jinja2` 替代简单的字符串格式化，以支持复杂逻辑。
*   **拒绝的建议**: 拒绝了 AI 推荐的 `Celery` (过重) 和 `PostgreSQL Transactional Outbox` (MVP 复杂度过高)。

详细设计请参考 `tutorial.md` (原始设计文档)。
