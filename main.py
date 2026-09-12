# -*- coding: utf-8 -*-
"""
主入口
------
1. 支持控制台输入产品信息，一键运行整套「主控 + 5 子 Agent」串行链路。
2. 内置示例测试用例（--demo）：产品=室内环境监测传感器，目标客户=弱电集成商、写字楼物业。
3. 运行结束后，将最终报告保存到本地 marketing_report.md 文件。
"""

import sys

from agents import MarketingAgentSystem


def build_report(product_name, target_customer, results):
    """把各阶段输出按固定结构组装为最终 Markdown 报告"""
    return f"""# {product_name} B端营销策划文档

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


def run_and_save(product_name, target_customer, product_desc=""):
    """一键运行整套链路并保存报告"""
    system = MarketingAgentSystem()
    results = system.run(product_name, target_customer, product_desc)

    report = build_report(product_name, target_customer, results)

    with open("marketing_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n最终报告已保存到 marketing_report.md")
    return report


def run_interactive():
    """交互式：控制台输入产品信息"""
    print("=" * 60)
    print("多 Agent B 端产品营销策划文档自动生成系统")
    print("=" * 60)

    product_name = input("请输入 B 端产品名称（如：室内环境监测传感器）：").strip()
    target_customer = input("请输入目标 B 端客户（如：弱电集成商、写字楼物业）：").strip()
    product_desc = input("请输入产品补充描述（可选，直接回车跳过）：").strip()

    # 空输入兜底
    if not product_name:
        product_name = "室内环境监测传感器"
    if not target_customer:
        target_customer = "弱电集成商、写字楼物业"

    run_and_save(product_name, target_customer, product_desc)


def run_demo():
    """示例测试用例：无需输入，直接运行演示"""
    print("运行示例测试用例 ...\n")
    run_and_save(
        product_name="室内环境监测传感器",
        target_customer="弱电集成商、写字楼物业",
        product_desc="一款用于室内空气质量（PM2.5、CO2、温湿度、甲醛）实时监测与告警的物联网传感器，"
                     "支持 Modbus/RS485 与云平台接入，可对接既有楼宇自控系统。",
    )


if __name__ == "__main__":
    # 支持两种启动方式：
    #   python main.py          -> 交互式输入
    #   python main.py --demo   -> 直接运行示例测试用例
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        run_interactive()
