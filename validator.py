# -*- coding: utf-8 -*-
"""
结构化校验模块
--------------
功能：代码自动检查子 Agent 输出是否包含指定标题；
若缺失，自动重试当前 Agent，最多重试 2 次（首次执行 + 2 次重试）。

log_cb 说明：
    可选回调函数，用于把「通过/重试/警告」等状态信息传给外部（例如 Streamlit 界面）。
    命令行模式下不传 log_cb，则沿用 print 打印到终端。
"""


class StructureValidator:
    """对 LLM 输出做结构化校验，缺失标题则自动重试"""

    def __init__(self, llm, max_retries=2):
        # llm: 已构建好的 LLM 客户端（langchain 的 ChatOpenAI 实例）
        self.llm = llm
        self.max_retries = max_retries

    def run(self, agent_name, prompt, required_headings, log_cb=None):
        """
        运行子 Agent 并校验输出结构。

        :param agent_name:       子 Agent 名称（用于日志打印）
        :param prompt:           发送给 LLM 的完整 prompt
        :param required_headings: 必须包含的标题列表（如 ["## 产品核心卖点", ...]）
        :param log_cb:           可选回调，接收状态信息字符串
        :return: 校验通过的输出文本
        """

        # 统一日志出口：有回调走回调，无回调走 print
        def log(msg):
            if log_cb:
                log_cb(msg)
            else:
                print(msg)

        current_prompt = prompt
        last_response = ""

        # 首次执行 + 最多 max_retries 次重试
        for attempt in range(self.max_retries + 1):
            last_response = self._call_llm(current_prompt)

            # 检查哪些必需标题缺失
            missing = [h for h in required_headings if h not in last_response]

            # 无缺失 => 校验通过，直接返回
            if not missing:
                log(f"✅ {agent_name} 输出结构校验通过")
                return last_response

            # 有缺失 => 把缺失标题告知模型，追加到 prompt 尾部后重试
            log(f"⚠️ {agent_name} 缺少标题 {missing}，进行第 {attempt + 1} 次重试")
            current_prompt = (
                prompt
                + f"\n\n【强制要求】你上一次的输出缺少以下必需标题：{missing}。"
                  f"请严格按指定 Markdown 结构完整重新输出，不得遗漏任何标题。"
            )

        # 重试耗尽仍不完整：返回最后一次输出，避免程序中断（可观测到问题）
        log(f"⚠️ {agent_name} 重试 {self.max_retries} 次后结构仍不完整，返回最后输出")
        return last_response

    def _call_llm(self, prompt):
        """调用 LLM 并返回其文本内容"""
        result = self.llm.invoke(prompt)
        return result.content
