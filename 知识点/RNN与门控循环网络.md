# 序列模型与门控机制（RNN → LSTM → GRU）

> 掌握度：🟡 接触过 ｜ 所属模块：序列模型与注意力

## 一句话直觉
处理文本、语音或时间序列时，数据具有**前后关联的“上下文时间轴”**。朴素 RNN 就像一个**患有短期健忘症的人**（时间步一长，前面的记忆就迅速遗忘殆尽）；LSTM（长短期记忆网络）给大脑装上了**三个精密阀门（遗忘门、输入门、输出门）和一个细胞状态高速传送带（Cell State）**，能够将上百步之前的关键历史信息无损传递；而 GRU 则是将结构精简为两个门（重置门、更新门）的轻量化高效版本。

---

## 核心要点与数学公式

### 1. 经典循环神经网络（Vanilla RNN）
- **隐藏状态更新公式**：
  $$h_t = \tanh(W_{hh} h_{t-1} + W_{xh} x_t + b_h)$$
- **致命痛点：BPTT（随时间反向传播）梯度消失与爆炸**：
  反向求导时需要连乘 $T$ 个 $W_{hh}^T \text{diag}(1 - h_t^2)$，当序列长度 $T > 50$ 时，梯度呈指数级衰减归零，无法捕获长程依赖（Long-term Dependency）。

---

### 2. LSTM 三门一传送带数学方程

```
        ┌──────────────────────── 传送带 Cell State (C_t) ────────────────────────┐
        │                                 ▲ (+)                                    ▼
        │                                 │  │                                     │
   C_{t-1} ──▶ [×] ───────────────┬───────┴──┴──────────────────────────────────▶ C_t
                ▲                 ▲          ▲                                     │
                │                 │          │ (候选值 c~_t)                        ▼
            [遗忘门 f_t]      [输入门 i_t]  [tanh]                             [tanh] ──▶ [×] ──▶ h_t
                ▲                 ▲          ▲                                     ▲
                └─────────────────┴──────────┴───────────────── [输出门 o_t] ──────┘
```

1. **遗忘门（Forget Gate）**：决定丢弃多少过去的记忆：
   $$f_t = \sigma(W_f [h_{t-1}, x_t] + b_f)$$
2. **输入门（Input Gate）与候选记忆**：决定将多少新信息存入传送带：
   $$i_t = \sigma(W_i [h_{t-1}, x_t] + b_i), \quad \tilde{C}_t = \tanh(W_c [h_{t-1}, x_t] + b_c)$$
3. **细胞状态更新（Cell State）**：线性相加保证梯度无阻碍流动：
   $$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$$
4. **输出门（Output Gate）与当前隐藏状态**：
   $$o_t = \sigma(W_o [h_{t-1}, x_t] + b_o), \quad h_t = o_t \odot \tanh(C_t)$$

---

## 最小验证代码（PyTorch LSTM 文本序列提取）

```python
import torch
import torch.nn as nn

# 模拟 1 个 Batch 包含 2 个句子, 每句话 5 个词, 词嵌入维度 10
# 输入张量形状: [Batch=2, Seq_Len=5, Input_Dim=10]
inputs = torch.randn(2, 5, 10)

# 定义 LSTM 单元 (输入10维, 隐藏状态20维, batch_first=True)
lstm = nn.LSTM(input_size=10, hidden_size=20, batch_first=True)

# 前向传播 (返回所有时间步的输出 与 最终的隐藏状态/细胞状态)
output, (hn, cn) = lstm(inputs)

print("所有时刻输出序列形状 (output):", output.shape) # [2, 5, 20]
print("最终时刻隐藏状态 (hn):", hn.shape)              # [1, 2, 20]
print("最终时刻细胞状态 (cn):", cn.shape)              # [1, 2, 20]
```

---

## 思考与自测

- **自测 1**：LSTM 是如何从数学上彻底克服传统 RNN 的梯度消失问题的？
  > *解析*：核心在于细胞状态传送带 $C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$。反向传播求导时，$\frac{\partial C_t}{\partial C_{t-1}} = f_t$。只要遗忘门 $f_t \approx 1$，梯度在传送带上就是以**线性常数直接向前传递**（类似 ResNet 的残差加法），避免了矩阵连续连乘带来的指数级衰减。

---

## 关联知识
- [[seq2seq与编码解码]]：基于 RNN/LSTM 的机器翻译经典框架。
- [[注意力机制]]：打破 RNN 循环瓶颈、开启 Transformer 时代的飞跃。
