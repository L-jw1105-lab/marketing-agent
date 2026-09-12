# -*- coding: utf-8 -*-
"""
市场研究与分析 Agent —— Streamlit 网页界面
==========================================
功能：
  1. 顶部标题「市场研究与分析 Agent」+ 模式切换（市场研究 / 营销策划）。
  2. 输入区：用户填写研究主题（或产品信息），点击「开始分析」。
  3. 展示区：实时显示 Agent 执行进度，最后把 Markdown 报告渲染到页面。
  4. 侧边栏：历史记录（每次生成的报告都会保存，可随时点击查看）。

启动方式（本地）：
    streamlit run app.py
"""

import streamlit as st

from agents import MarketingAgentSystem, ResearchAgentSystem

# ==================== 页面基础配置 ====================
# 必须是第一个 st 命令：设置页面标题、图标、宽屏布局
st.set_page_config(
    page_title="市场研究与分析 Agent",
    page_icon="📊",
    layout="wide",
)

# ==================== 自定义 CSS（让界面更专业美观） ====================
st.markdown(
    """
    <style>
        /* 顶部主标题区域 */
        .main-title {
            font-size: 2.4rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            font-size: 1rem;
            color: #6b7280;
            margin-bottom: 1.5rem;
        }
        /* 分区标题 */
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1a1a2e;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        /* 底部说明 */
        .footer {
            text-align: center;
            color: #9ca3af;
            font-size: 0.85rem;
            margin-top: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================== 顶部标题 ====================
st.markdown('<div class="main-title">📊 市场研究与分析 Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">多智能体串行协作 · 自动生成结构化市场研究报告 / 营销策划方案</div>',
    unsafe_allow_html=True,
)

# ==================== 侧边栏：模式切换 + 历史记录 ====================
with st.sidebar:
    st.markdown("## ⚙️ 分析模式")
    # 模式切换：市场研究 / 营销策划
    mode = st.radio(
        "请选择分析模式",
        options=["市场研究", "营销策划"],
        index=0,
        help="市场研究：输入研究主题；营销策划：输入 B 端产品信息",
    )

    st.markdown("---")
    st.markdown("## 🕘 历史记录")

    # 历史记录存储在 session_state 中（列表，每个元素是一个 dict）
    if "history" not in st.session_state:
        st.session_state.history = []

    # 展示历史记录：点击任意一条可查看对应报告
    if st.session_state.history:
        # 倒序展示（最新的在最上面）
        for i, item in enumerate(reversed(st.session_state.history)):
            # 每个历史项做成一个可点击按钮，点击后把该报告载入查看区
            label = f"📄 {item['title']}"
            if st.button(label, key=f"hist_{i}", use_container_width=True):
                st.session_state.current_report = item["report"]
                st.session_state.current_title = item["title"]
    else:
        st.caption("暂无历史记录")

# ==================== 主区域：输入区 ====================
st.markdown('<div class="section-title">📝 输入区</div>', unsafe_allow_html=True)

# 根据模式显示不同的输入框
if mode == "市场研究":
    # 市场研究模式：只需要一个「研究主题」输入框
    topic = st.text_input(
        "请输入研究主题",
        placeholder="例如：抖音零食带货、新能源汽车出海、宠物经济……",
        key="topic_input",
    )
else:
    # 营销策划模式：产品名 + 目标客户 + 可选描述（三个输入框）
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input(
            "产品名称",
            placeholder="例如：室内环境监测传感器",
            key="product_name_input",
        )
    with col2:
        target_customer = st.text_input(
            "目标 B 端客户",
            placeholder="例如：弱电集成商、写字楼物业",
            key="target_input",
        )
    product_desc = st.text_area(
        "产品补充描述（可选）",
        placeholder="补充说明产品的功能、技术特点、应用场景等……",
        key="desc_input",
        height=80,
    )

# 「开始分析」按钮（居中显示）
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    start_clicked = st.button("🚀 开始分析", type="primary", use_container_width=True)

# ==================== 主区域：展示区 ====================
st.markdown('<div class="section-title">📄 分析结果</div>', unsafe_allow_html=True)

# 结果展示容器（用于实时刷新进度与最终报告）
result_container = st.container()


def run_research(topic):
    """
    执行「市场研究」流程，实时展示进度，最后返回报告。
    进度机制：用一个空占位符 status_placeholder 实时刷新文字，用进度条展示整体完成度。
    """
    with result_container:
        # 清空旧内容，新建进度展示占位符
        status_placeholder = st.empty()
        progress_bar = st.progress(0.0)

    # 进度回调：LLM 每完成一步都会调用此函数更新界面
    def on_progress(msg):
        status_placeholder.info(msg)

    # 创建研究系统，传入进度回调
    system = ResearchAgentSystem(progress_cb=on_progress)

    # 执行完整流程（进度回调会实时更新界面）
    results = system.run(topic)

    # 流程结束后，进度条拉满、状态更新为完成
    progress_bar.progress(1.0)
    status_placeholder.success("✅ 研究完成")

    # 组装最终报告（Markdown）
    report = f"""# {topic} 市场研究报告

{results['overview']}

---

{results['collected']}

---

{results['analysis']}

---

{results['competitor']}

---

{results['report']}
"""
    return report, f"{topic}（市场研究）"


def run_marketing(product_name, target_customer, product_desc):
    """
    执行「营销策划」流程，实时展示进度，最后返回报告。
    """
    with result_container:
        status_placeholder = st.empty()
        progress_bar = st.progress(0.0)

    def on_progress(msg):
        status_placeholder.info(msg)

    system = MarketingAgentSystem(progress_cb=on_progress)

    # 执行完整流程（进度回调会实时更新界面）
    results = system.run(product_name, target_customer, product_desc)

    progress_bar.progress(1.0)
    status_placeholder.success("✅ 营销策划完成")

    # 组装最终报告（与 main.py 的 build_report 保持一致）
    report = f"""# {product_name} B端营销策划文档

> 目标 B 端客户：{target_customer}

{results['overview']}

---

{results['selling_points']}

---

{results['activities']}

---

{results['copy_texts']}

---

{results['validation']}

---

{results['effect']}
"""
    return report, f"{product_name}（营销策划）"


# ==================== 处理「开始分析」按钮点击 ====================
if start_clicked:
    # 输入校验
    if mode == "市场研究" and not topic.strip():
        st.warning("⚠️ 请输入研究主题")
    elif mode == "营销策划" and (not product_name.strip() or not target_customer.strip()):
        st.warning("⚠️ 请填写产品名称和目标客户")
    else:
        try:
            # 执行对应流程，拿到最终报告
            if mode == "市场研究":
                report, title = run_research(topic.strip())
            else:
                report, title = run_marketing(
                    product_name.strip(), target_customer.strip(), product_desc.strip()
                )

            # 保存到历史记录（保留最近 20 条）
            st.session_state.history.append({"title": title, "report": report})
            if len(st.session_state.history) > 20:
                st.session_state.history.pop(0)

            # 把当前报告存入 session_state，供展示区渲染
            st.session_state.current_report = report
            st.session_state.current_title = title

        except Exception as e:
            st.error(f"❌ 分析过程出错：{e}")

# ==================== 展示区：渲染当前报告 ====================
with result_container:
    # 如果存在「当前报告」，就渲染它
    if "current_report" in st.session_state and st.session_state.current_report:
        st.markdown("### " + st.session_state.current_title)
        st.markdown("---")
        # 用 st.markdown 渲染 Markdown 报告
        st.markdown(st.session_state.current_report, unsafe_allow_html=False)
    else:
        # 未点击时的占位提示
        st.info("👆 请在上方输入内容并点击「开始分析」，生成的报告将显示在这里。")

# ==================== 底部 ====================
st.markdown(
    '<div class="footer">多 Agent 串行协作 · Python + LangChain + Streamlit</div>',
    unsafe_allow_html=True,
)
