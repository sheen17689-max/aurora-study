# AutoGen 对话协同（Microsoft AutoGen）

> 掌握度：🟡 接触过

## 一句话直觉
AutoGen 是微软推出的**“群聊式多智能体协同引擎”**：在 AutoGen 的哲学里，**「一切皆是对话」**。程序员 Agent、代码执行沙箱 Agent、产品经理 Agent 就像在一个企业微信群里，大家轮流发消息交流；代码写错了，沙箱直接把报错发进群，程序员看到后自动发消息修正代码，直到打出 'TERMINATE' 结案。

---

## 📌 ConversableAgent 对话驱动模式

- **ConversableAgent**：具备发送消息、接收消息并触发回复回调（Reply Functions）的统一抽象；
- **UserProxyAgent**：代表人类用户的代理，负责代理执行本地 Python 代码或等待人类输入；
- **GroupChat & GroupChatManager**：多方群聊中枢，利用大模型自适应决定下一个发言者是谁。

---

## 思考与自测
- 微软 AutoGen 的对话驱动架构（Everything is a Conversation）相比传统的硬编码工作流有哪些独特的灵活性？
- 在 AutoGen 群聊中，有哪些机制可以决定「下一个发言人是谁」（如 Round Robin、LLM 判定、Random）？
- AutoGen 早期版本在执行任意 Python 代码时的安全风险如何防范？\n