# -*- coding: utf-8 -*-
"""
Agent 模块
----------
1. 封装 LLM 客户端（基于 langchain 的 ChatOpenAI，可替换为豆包/DeepSeek 等）。
2. 定义「主控 Agent + 5 个子 Agent」以及它们的串行编排逻辑。
   业务依赖关系：卖点 → 活动方案 → 文案 → 文案校验 → 效果评估（必须串行，不能并行）。
"""

from langchain_openai import ChatOpenAI

import config
import prompts
from validator import StructureValidator

# ==================== 各子 Agent 输出必须包含的标题 ====================
# 用于结构化校验模块：若 LLM 输出缺少这些标题，则自动重试。
REQUIRED_HEADINGS = {
    "卖点挖掘子Agent": ["## 产品核心卖点", "## 产品次要卖点"],
    "营销活动策划子Agent": ["## 活动方案一：新品试用拉新活动", "## 活动方案二：批量集采阶梯增收活动"],
    "多渠道文案生成子Agent": ["## 海报文案", "## B端商品详情文案", "## 朋友圈文案", "## 社群推广文案"],
    "文案风格&合规校验子Agent": ["## 风格校验结果", "## 合规校验结果", "## 修改建议"],
    "营销效果预估子Agent": ["## 文案与活动效果预估", "## 潜在风险", "## 优化建议"],
}


def build_llm():
    """构建 LLM 客户端。

    说明：这里使用 langchain 的 ChatOpenAI，它遵循 OpenAI 协议。
    替换为豆包/DeepSeek/通义千问等模型时，只需修改 config.py 里的
    BASE_URL 与 MODEL_NAME，本函数无需改动。
    """
    return ChatOpenAI(
        api_key=config.API_KEY,
        base_url=config.BASE_URL,   # 兼容 OpenAI 协议的接口地址
        model=config.MODEL_NAME,
        temperature=config.TEMPERATURE,
    )


class MarketingAgentSystem:
    """主控 + 5 子 Agent 串行协作系统"""

    def __init__(self, progress_cb=None):
        self.llm = build_llm()
        # progress_cb: 可选进度回调函数，用于 Streamlit 实时展示执行进度
        self.progress_cb = progress_cb
        self.validator = StructureValidator(self.llm, max_retries=config.MAX_RETRIES)

    def _notify(self, msg):
        """统一进度输出：有回调走回调，无回调走 print（保持命令行可用）"""
        if self.progress_cb:
            self.progress_cb(msg)
        else:
            print(msg)

    # ---------- 主控 Agent：生成项目概述 ----------
    def master_overview(self, product_name, target_customer, product_desc):
        prompt = prompts.MASTER_PROMPT + (
            f"\n\n本次用户输入如下：\n"
            f"【产品名称】{product_name}\n"
            f"【目标 B 端客户】{target_customer}\n"
            f"【产品补充描述】{product_desc or '无'}\n"
        )
        return self._call(prompt)

    # ---------- ① 卖点挖掘子 Agent ----------
    def agent_selling_points(self, product_name, target_customer, product_desc):
        prompt = prompts.SELLING_POINT_PROMPT.format(
            product_name=product_name,
            target_customer=target_customer,
            product_desc=product_desc or "无",
        )
        return self.validator.run("卖点挖掘子Agent", prompt, REQUIRED_HEADINGS["卖点挖掘子Agent"], log_cb=self._notify)

    # ---------- ② 营销活动策划子 Agent（依赖 ① 卖点输出） ----------
    def agent_activities(self, product_name, target_customer, selling_points):
        prompt = prompts.ACTIVITY_PROMPT.format(
            product_name=product_name,
            target_customer=target_customer,
            selling_points=selling_points,
        )
        return self.validator.run("营销活动策划子Agent", prompt, REQUIRED_HEADINGS["营销活动策划子Agent"], log_cb=self._notify)

    # ---------- ③ 多渠道文案生成子 Agent（依赖 ①② 输出） ----------
    def agent_copywriting(self, product_name, target_customer, selling_points, activities):
        prompt = prompts.COPY_PROMPT.format(
            product_name=product_name,
            target_customer=target_customer,
            selling_points=selling_points,
            activities=activities,
        )
        return self.validator.run("多渠道文案生成子Agent", prompt, REQUIRED_HEADINGS["多渠道文案生成子Agent"], log_cb=self._notify)

    # ---------- ④ 文案风格&合规校验子 Agent（依赖 ③ 文案输出） ----------
    def agent_validation(self, copy_texts):
        prompt = prompts.VALIDATION_PROMPT.format(copy_texts=copy_texts)
        return self.validator.run("文案风格&合规校验子Agent", prompt, REQUIRED_HEADINGS["文案风格&合规校验子Agent"], log_cb=self._notify)

    # ---------- ⑤ 营销效果预估子 Agent（依赖 ①②③ 输出） ----------
    def agent_effect(self, product_name, target_customer, selling_points, activities, copy_texts):
        prompt = prompts.EFFECT_PROMPT.format(
            product_name=product_name,
            target_customer=target_customer,
            selling_points=selling_points,
            activities=activities,
            copy_texts=copy_texts,
        )
        return self.validator.run("营销效果预估子Agent", prompt, REQUIRED_HEADINGS["营销效果预估子Agent"], log_cb=self._notify)

    # ---------- 串行编排主流程 ----------
    def run(self, product_name, target_customer, product_desc=""):
        """
        主控串行调度 5 个子 Agent，返回各阶段输出的字典。
        串行关键：每一步都拿到上一步的返回结果作为入参，天然无法并行。
        """
        self._notify(f"🚀 开始执行：{product_name} 的 B 端营销策划")

        # 主控 Agent：项目概述
        self._notify("📋 正在生成项目概述 ...")
        overview = self.master_overview(product_name, target_customer, product_desc)

        # ① 卖点挖掘
        self._notify("🎯 正在挖掘产品卖点 ...")
        selling_points = self.agent_selling_points(product_name, target_customer, product_desc)

        # ② 活动策划（依赖 ①）
        self._notify("📅 正在策划营销活动方案 ...")
        activities = self.agent_activities(product_name, target_customer, selling_points)

        # ③ 文案生成（依赖 ①②）
        self._notify("✍️ 正在生成多渠道文案 ...")
        copy_texts = self.agent_copywriting(product_name, target_customer, selling_points, activities)

        # ④ 文案校验（依赖 ③）
        self._notify("🔍 正在进行文案风格与合规校验 ...")
        validation = self.agent_validation(copy_texts)

        # ⑤ 效果预估（依赖 ①②③）
        self._notify("📈 正在预估营销效果与风险 ...")
        effect = self.agent_effect(product_name, target_customer, selling_points, activities, copy_texts)

        self._notify("✅ 全部子 Agent 串行执行完成")

        return {
            "overview": overview,
            "selling_points": selling_points,
            "activities": activities,
            "copy_texts": copy_texts,
            "validation": validation,
            "effect": effect,
        }

    def _call(self, prompt):
        """直接调用 LLM 并返回文本"""
        return self.llm.invoke(prompt).content


# ==================== 市场研究 Agent 输出必须包含的标题 ====================
RESEARCH_REQUIRED_HEADINGS = {
    "资料搜集子Agent": ["## 市场规模与增长", "## 用户画像与需求", "## 产业链与渠道结构", "## 政策与外部环境"],
    "市场分析子Agent": ["## 市场需求分析", "## 供给现状分析", "## 市场趋势与机会"],
    "竞品分析子Agent": ["## 主要竞争参与者", "## 典型竞争策略", "## 差异化机会与启示"],
    "报告撰写子Agent": ["## 研究结论", "## 关键发现", "## 策略建议", "## 风险提示"],
}


class ResearchAgentSystem:
    """市场研究 Agent：主控 + 4 子 Agent 串行协作（搜集 → 分析 → 竞品 → 报告）"""

    def __init__(self, progress_cb=None):
        self.llm = build_llm()
        self.progress_cb = progress_cb
        self.validator = StructureValidator(self.llm, max_retries=config.MAX_RETRIES)

    def _notify(self, msg):
        """统一进度输出：有回调走回调，无回调走 print"""
        if self.progress_cb:
            self.progress_cb(msg)
        else:
            print(msg)

    # ---------- 主控：研究概述 ----------
    def master_overview(self, topic):
        prompt = prompts.RESEARCH_MASTER_PROMPT + f"\n\n本次研究主题：{topic}\n"
        return self.llm.invoke(prompt).content

    # ---------- ① 资料搜集 ----------
    def agent_collect(self, topic):
        prompt = prompts.RESEARCH_COLLECT_PROMPT.format(topic=topic)
        return self.validator.run("资料搜集子Agent", prompt, RESEARCH_REQUIRED_HEADINGS["资料搜集子Agent"], log_cb=self._notify)

    # ---------- ② 市场分析（依赖 ①） ----------
    def agent_analysis(self, topic, collected):
        prompt = prompts.RESEARCH_ANALYSIS_PROMPT.format(topic=topic, collected=collected)
        return self.validator.run("市场分析子Agent", prompt, RESEARCH_REQUIRED_HEADINGS["市场分析子Agent"], log_cb=self._notify)

    # ---------- ③ 竞品分析（依赖 ②） ----------
    def agent_competitor(self, topic, analysis):
        prompt = prompts.RESEARCH_COMPETITOR_PROMPT.format(topic=topic, analysis=analysis)
        return self.validator.run("竞品分析子Agent", prompt, RESEARCH_REQUIRED_HEADINGS["竞品分析子Agent"], log_cb=self._notify)

    # ---------- ④ 报告撰写（依赖 ①②③） ----------
    def agent_report(self, topic, collected, analysis, competitor):
        prompt = prompts.RESEARCH_REPORT_PROMPT.format(
            topic=topic, collected=collected, analysis=analysis, competitor=competitor
        )
        return self.validator.run("报告撰写子Agent", prompt, RESEARCH_REQUIRED_HEADINGS["报告撰写子Agent"], log_cb=self._notify)

    # ---------- 串行编排主流程 ----------
    def run(self, topic):
        """主控串行调度 4 个子 Agent，返回各阶段输出字典"""
        self._notify(f"🚀 开始研究主题：{topic}")

        self._notify("📋 正在生成研究概述 ...")
        overview = self.master_overview(topic)

        self._notify("🔎 正在搜集市场资料 ...")
        collected = self.agent_collect(topic)

        self._notify("📊 正在分析市场趋势 ...")
        analysis = self.agent_analysis(topic, collected)

        self._notify("⚔️ 正在分析竞争格局 ...")
        competitor = self.agent_competitor(topic, analysis)

        self._notify("📝 正在撰写研究报告 ...")
        report = self.agent_report(topic, collected, analysis, competitor)

        self._notify("✅ 市场研究全流程执行完成")

        return {
            "overview": overview,
            "collected": collected,
            "analysis": analysis,
            "competitor": competitor,
            "report": report,
        }
