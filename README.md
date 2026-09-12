# 📊 市场研究与分析 Agent

一个基于 **Python + LangChain + Streamlit** 的多智能体（Multi-Agent）串行协作系统，自动生成结构化的**市场研究报告**或 **B 端营销策划方案**，并提供专业的网页界面。

## 一、功能特性

- **双模式**：
  - 📈 **市场研究**：输入一个研究主题（如「抖音零食带货」），自动完成「资料搜集 → 市场分析 → 竞品分析 → 报告撰写」。
  - 🎯 **营销策划**：输入 B 端产品信息，自动完成「卖点挖掘 → 活动策划 → 文案生成 → 合规校验 → 效果预估」。
- **多 Agent 串行协作**：上一个 Agent 的输出作为下一个 Agent 的输入，业务依赖天然串行。
- **结构化校验**：每个子 Agent 输出会自动检查是否包含指定标题，缺失则自动重试（最多 2 次）。
- **实时进度展示**：网页上实时显示执行进度（如「正在搜集市场资料…」「正在撰写报告…」）。
- **历史记录**：每次生成的报告保存在侧边栏，可随时点击查看。
- **Markdown 报告渲染**：最终报告以 Markdown 格式渲染在页面上，可直接阅读/复制。

## 二、项目结构

```
marketing-agent/
├── app.py               # Streamlit 网页界面（入口）
├── main.py              # 命令行入口（交互式 / --demo）
├── config.py            # 配置：API Key、接口地址、模型名、温度、重试次数
├── prompts.py           # 全部 Prompt（营销 6 套 + 研究 5 套）
├── agents.py            # LLM 客户端 + 主控/子 Agent 定义 + 串行编排
├── validator.py         # 结构化校验模块（缺失标题自动重试）
├── requirements.txt     # 依赖清单
├── README.md            # 本文件
└── 项目介绍.md           # 项目介绍文档
```

## 三、本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.py`，填入你的 API Key（默认已配置为 DeepSeek）：

```python
API_KEY = "你的Key"
BASE_URL = "https://api.deepseek.com/v1"   # 按平台修改
MODEL_NAME = "deepseek-chat"
```

> 支持 OpenAI / DeepSeek / 豆包 / 通义千问等所有「兼容 OpenAI 协议」的模型，只改 `BASE_URL` 和 `MODEL_NAME` 即可。

### 3. 启动网页界面

```bash
streamlit run app.py
```

启动后浏览器会自动打开 `http://localhost:8501`。

### 4. （可选）命令行运行

```bash
python main.py          # 交互式输入
python main.py --demo   # 运行内置示例
```

## 四、部署到 Streamlit Cloud（拿到公开网址）

Streamlit Cloud 是官方免费托管平台，部署后你会得到一个 `https://你的应用.streamlit.app` 的公开网址。

### 第 1 步：把代码上传到 GitHub

1. 在 [GitHub](https://github.com) 创建一个**公开**仓库（例如 `marketing-agent`）。
2. 把本项目的所有文件推送到该仓库：

```bash
git init
git add .
git commit -m "init: 市场研究与分析 Agent"
git branch -M main
git remote add origin https://github.com/你的用户名/marketing-agent.git
git push -u origin main
```

> 关键文件：`app.py`、`requirements.txt`、`config.py`、`prompts.py`、`agents.py`、`validator.py` 都要一起上传。

### 第 2 步：在 Streamlit Cloud 部署

1. 打开 [https://share.streamlit.io](https://share.streamlit.io)，用 GitHub 账号登录。
2. 点击 **New app** → 选择你刚才的 GitHub 仓库。
3. **Main file path** 填 `app.py`（这是 Streamlit 应用的入口文件）。
4. 点击 **Deploy**，等待 1~2 分钟即可。

### 第 3 步：配置 Secrets（API Key）

在 Streamlit Cloud 的 App 设置里，进入 **Settings → Secrets**，添加你的 API Key（这样 Key 不会暴露在公开代码里）：

```toml
OPENAI_API_KEY = "你的真实Key"
```

> 我们的 `config.py` 会优先从环境变量 `OPENAI_API_KEY` 读取，所以只要在 Secrets 里配好，代码里就不用写死 Key 了。

### 第 4 步：拿到公开网址

部署成功后，你会得到一个形如 `https://marketing-agent-xxxx.streamlit.app` 的网址，直接发给任何人即可访问。

## 五、常见问题

| 问题 | 解决 |
| --- | --- |
| 网页打不开 | 确认 `streamlit run app.py` 已启动，访问 `http://localhost:8501` |
| 提示缺少模块 | 运行 `pip install -r requirements.txt` |
| 分析过程报错 | 检查 `config.py` 的 API Key 和 BASE_URL 是否正确 |
| 部署后连不上 | 确认在 Streamlit Cloud Secrets 里配置了 `OPENAI_API_KEY` |
| 输出缺少某个标题 | 这是结构化校验自动重试的兜底；若仍缺失，检查对应 Prompt 的标题拼写 |
