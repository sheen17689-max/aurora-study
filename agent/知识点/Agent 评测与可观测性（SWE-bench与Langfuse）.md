# Agent 评测与基准测试（SWE-bench & GAIA）

> 掌握度：🟡 接触过

## 一句话直觉
Agent 评测就像给野生 AI 准备的**“国家级专业资格闭卷大考”**：在 Demo 阶段，看着模型跑通两个小例子很有成就感；但要检验它是不是真正的软件工程师或通用助理，必须把真实的 GitHub 历史 Issue（SWE-bench）或需要查网页/读 Excel 的综合长程难题（GAIA）甩给它，以严苛的单元测试打分论英雄。

---

## 📌 行业两大里程碑评测基准

1. **SWE-bench (Software Engineering Benchmark)**：
   - 提取自真实顶级开源 Python 库（如 django, sympy, scikit-learn）的真实 Pull Request 与 Issue；
   - 评测标准：Agent 自主阅读代码、定位 Bug、修改文件并**让所有的单元测试全部 PASS**。
2. **GAIA (General AI Assistants)**：
   - 考察跨模态、网页浏览、复杂推理的长程综合助理能力，被誉为检验通向 AGI 智能体的试金石。

---

## 思考与自测
- 为什么传统的 MMLU 或 GSM8K 等选择题测试已经无法有效度量现代自主 Agent 的真实能力？
- SWE-bench 的通过率（Pass@1）为什么长期被各大顶尖闭源与开源模型作为代码 Agent 的最高竞技场？
- 如何构建企业内部业务特化的 Agent 自动化回归评测数据集？\n