# 运行与部署指南 (Run & Deploy Guide)

## 1. 本地运行 (Local Execution)

你有两种方式运行本项目：使用 Docker（推荐）或直接使用 Python。

### 方式 A: 使用 Docker (推荐)
如果你已安装 Docker 和 Docker Compose，这是最简单的方法。

1.  **启动服务**
    在 `rc_project` 目录下打开终端，运行：
    ```bash
    docker-compose up --build
    ```
    这将启动 Redis, Web API (Port 8000), 和 Worker。

2.  **测试 API**
    打开浏览器访问: `http://localhost:8000/docs`
    你可以看到 Swagger UI。
    *   点击 `POST /api/v1/notify` -> `Try it out`
    *   Vendor ID 输入: `promos-ad-network`
    *   Payload 输入: `{"user_id": "123", "campaign": "summer_sale"}`
    *   点击 `Execute`。

3.  **查看日志**
    在终端中，你会看到 Worker 输出日志：`Notification delivered successfully...`

### 方式 B: 本地 Python 运行
如果你没有 Docker，你需要本地安装 Redis。

1.  **前置要求**
    *   安装 Python 3.9+
    *   安装 Redis Server 并启动 (默认端口 6379)

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **启动 Web Server**
    打开一个终端窗口：
    ```bash
    uvicorn app.main:app --reload
    ```

4.  **启动 Worker**
    打开另一个终端窗口：
    ```bash
    python -m app.worker
    # 或者直接使用 rq 命令
    # rq worker default --url redis://localhost:6379/0
    ```

## 2. 部署到 Git (Deploy to Git)

将代码提交到 Github 仓库。

1.  **初始化 Git 仓库**
    在 `rc_project` 目录下：
    ```bash
    git init
    ```

2.  **配置 .gitignore**
    创建 `.gitignore` 文件，防止提交垃圾文件：
    ```gitignore
    __pycache__/
    *.pyc
    .env
    venv/
    ```

3.  **提交代码**
    ```bash
    git add .
    git commit -m "Initial commit of API Notification Gateway MVP"
    ```

4.  **推送到 GitHub**
    *   在 GitHub 上创建一个新的仓库，名称为 `rc_{your_nickname}` (例如 `rc_antigravity`)。
    *   复制仓库地址 (例如 `https://github.com/ypskiy/rc_runxi_zhou.git`)。
    *   运行以下命令：
    ```bash
    git branch -M main
    git remote add origin https://github.com/ypskiy/rc_runxi_zhou.git
    git push -u origin main
    ```

## 3. 常见问题
*   **Redis 连接失败**: 检查 `app/config.py` 中的 `REDIS_URL`，或者确保 Docker/本地 Redis 正在运行。
*   **Vendor ID Unknown**: 确保请求中的 `vendor_id` 存在于 `app/config.py` 的字典中。
