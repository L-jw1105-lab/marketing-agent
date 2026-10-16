# -*- coding: utf-8 -*-
"""
配置模块
--------
集中管理 LLM 的 API Key、接口地址、模型名、温度、重试次数等。

若需要把 LLM 从 OpenAI 替换为豆包(Doubao)/DeepSeek/通义千问等
「兼容 OpenAI 协议」的大模型，只需修改下方 BASE_URL 和 MODEL_NAME 即可，
其余代码完全不用改动。
"""

import os

# ==================== LLM 配置（按需修改） ====================

# 你的 API Key：
#   - 优先从环境变量 OPENAI_API_KEY 读取；
#   - 若环境变量不存在，则使用下方默认占位符（请改成你的真实 Key）。
import streamlit as st
API_KEY = st.secrets["DEEPSEEK_API_KEY"]
# 接口地址（OpenAI 官方）：
#   - 替换为豆包/火山方舟：  "https://ark.cn-beijing.volces.com/api/v3"
#   - 替换为 DeepSeek：      "https://api.deepseek.com/v1"
#   - 替换为通义千问兼容：    "https://dashscope.aliyuncs.com/compatible-mode/v1"
BASE_URL = "https://api.deepseek.com/v1"

# 模型名（按所选平台填写）：
#   - OpenAI：  gpt-4o-mini / gpt-4o
#   - 豆包：    doubao-pro-32k / doubao-lite-32k
#   - DeepSeek：deepseek-chat
MODEL_NAME = "deepseek-chat"

# 温度：越低输出越稳定、越符合结构化要求（B 端营销文案建议 0.3）
TEMPERATURE = 0.3

# 结构化校验失败时的最大重试次数（需求固定为 2）
MAX_RETRIES = 2
