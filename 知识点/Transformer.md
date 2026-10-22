# Transformer 架构与大模型基石

> 掌握度：🟡 接触过 ｜ 所属模块：序列模型与注意力

## 一句话直觉
Transformer 是**“彻底摒弃循环与卷积、纯靠注意力机制构建的现代大模型总图纸”**（GPT-4、Claude、LLaMA、BERT 乃至 Vision Transformer 视觉模型的共同母体）：它通过**并行自注意力（Self-Attention）**让所有词在一瞬间互相“一眼看透全部上下文”，彻底打破了 RNN 无法并行训练的物理枷锁，开启了大算力海量数据训练大模型的时代。

---

## 核心要点与数学公式

### 1. Transformer 标准宏观架构（Attention Is All You Need）

```
【Encoder Block (编码器层)】                     【Decoder Block (解码器层)】
  输入嵌入 + 位置编码 (Positional Encoding)         输出嵌入 + 位置编码
        │                                                  │
  ┌─────▼─────────────────────────┐                ┌───────▼─────────────────────────┐
  │ 1. Multi-Head Self-Attention  │                │ 1. Masked Self-Attention (因果) │
  │    + 残差相加 & LayerNorm (LN) │                │    + 残差相加 & LayerNorm       │
  ├───────────────────────────────┤                ├─────────────────────────────────┤
  │ 2. Feed-Forward Network (FFN) │                │ 2. Cross-Attention (查 Encoder)  │
  │    + 残差相加 & LayerNorm     │ ──▶ (K, V) ──▶ │    + 残差相加 & LayerNorm       │
  └───────────────────────────────┘                ├─────────────────────────────────┤
                                                   │ 3. Feed-Forward Network (FFN)   │
                                                   │    + 残差相加 & LayerNorm       │
                                                   └─────────────────────────────────┘
```

---

### 2. 关键组件与技术细节

1. **位置编码（Positional Encoding）**：
   - 因为自注意力机制具有**排列置换不变性（Permutation Invariant）**（词的顺序打乱点积结果完全一样），必须显式给每个位置注入位置坐标正余弦波信号：
     $$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right), \quad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)$$
2. **前馈全连接网络（FFN）**：
   - 每个 Attention 后面必须紧跟一个 2 层的 [[多层感知机]]（中间维度扩大 4 倍），大模型的“知识记忆库”绝大部分沉淀于此：
     $$\text{FFN}(x) = \max(0, x W_1 + b_1) W_2 + b_2$$
3. **因果掩码（Causal Mask / 下三角掩码）**：
   - Decoder 在自回归生成时，必须将未来时间步的 Attention 分数加上 $-\infty$ 强制置零，**防止模型作弊偷看未来的答案**。
4. **Pre-LN vs Post-LN 架构演化**：
   - 原始论文采用 Post-LN（在残差相加后做 LN，深层极易发散）；现代主流大模型全部采用 **Pre-LN（在进入注意力前做 LN，训练极其平稳）**。

---

## 最小验证代码（PyTorch 核心 TransformerEncoderLayer）

```python
import torch
import torch.nn as nn

# 1. 模拟输入序列: [Batch=2, Seq_Len=8, D_model=64]
src = torch.randn(2, 8, 64)

# 2. 定义单个 Transformer 编码器层 (4个多头, 前馈隐藏维度256, Pre-LN)
encoder_layer = nn.TransformerEncoderLayer(
    d_model=64, nhead=4, dim_feedforward=256, norm_first=True, batch_first=True
)

# 3. 前向计算
output = encoder_layer(src)
print("Transformer 编码输出形状:", output.shape) # [2, 8, 64]
```

---

## 思考与自测

- **自测 1**：为什么在 NLP 和 Transformer 中统一使用 Layer Normalization（LN），而不使用视觉中常见的 Batch Normalization（BN）？
  > *解析*：
  > 1. NLP 文本序列长度不一（有长有短存在大量的 Padding 填充 0），BN 沿 Batch 维度统计会被 Padding 严重污染；
  > 2. LN 沿着单个样本内部的特征隐藏维度（`D_model`）独立做归一化，**完全不依赖 Batch 大小与其他样本**，单条样本推理或大批次训练均保持高度一致。

---

## 关联知识
- [[注意力机制]]：Transformer 的核心引擎组件。
- [[多层感知机]]：FFN 前馈子层在 Transformer 中的结构。
- [[Batch Normalization]]：与 Layer Normalization 的设计理念对比。
