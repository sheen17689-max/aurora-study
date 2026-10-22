# Seq2Seq 与编码-解码架构（Encoder-Decoder Architecture）

> 掌握度：🟡 接触过 ｜ 所属模块：序列模型与注意力

## 一句话直觉
Seq2Seq（Sequence-to-Sequence）是处理**“输入输出长度不固定的序列变换任务”的通用范式**（如中英翻译、文本摘要、语音识别、问答系统）。它就像一个**“同声传译员”**：**编码器（Encoder）负责认真听完并理解整段中文**，将其浓缩压缩为一个高维语义上下文向量（Context Vector）；**解码器（Decoder）负责拿到这个语义中枢**，一个词一个词地顺畅吐出英文翻译。

---

## 核心要点与数学公式

### 1. 经典 Encoder-Decoder 架构流图

```
【源句子输入 (中文)】: "我" ──▶ "爱" ──▶ "深度学习"
                       │        │         │
                       ▼        ▼         ▼
【Encoder (编码器)】: [RNN] ──▶ [RNN] ──▶ [RNN] ──▶ 语义压缩向量 C (Context Vector / 瓶颈)
                                                            │
                                                            ▼
【Decoder (解码器)】: [<BOS>] ──▶ [RNN] ──▶ [RNN] ──▶ [RNN] ──▶ [<EOS>]
                                    │        │        │
                                    ▼        ▼        ▼
【目标翻译输出 (英文)】:          "I"     "love"    "AI"
```

---

### 2. 传统 Seq2Seq 的致命短板：信息瓶颈（Information Bottleneck）
- 不管输入句子是 5 个词还是 1000 个词的长文档，传统 Seq2Seq 都强制将其**压缩为固定长度的单一向量 $C$**（如 512 维）。
- **灾难后果**：长句子的早期信息被严重稀释丢失，机器翻译在超过 20 个词时 BLEU 分数断崖式下跌。
- **解决方案**：引入 **[[注意力机制]]**，让解码器在生成每个词时，能够动态回看编码器所有时刻的特征状态！

---

### 3. 训练阶段技巧：Teacher Forcing
- **训练时**：解码器在第 $t$ 步的输入不是模型在第 $t-1$ 步瞎猜的词，而是**直接喂入真实的标签词（Ground Truth）**，大幅加快训练收敛速度；
- **推理时（自回归生成）**：没有真实标签，只能将前一步模型实际生成的词（$\hat{y}_{t-1}$）作为下一步的输入，直到生成结束符 `<EOS>`。

---

## 最小验证代码（PyTorch 结构框架）

```python
import torch
import torch.nn as nn

class ToySeq2Seq(nn.Module):
    def __init__(self, vocab_size=100, embed_dim=32, hidden_dim=64):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.encoder = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.decoder = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc_out = nn.Linear(hidden_dim, vocab_size)

    def forward(self, src, trg):
        # src: [Batch, Src_Len], trg: [Batch, Trg_Len]
        src_emb = self.embed(src)
        _, hidden = self.encoder(src_emb) # 获取 Encoder 最终语义状态
        
        trg_emb = self.embed(trg)
        dec_out, _ = self.decoder(trg_emb, hidden) # 将语义向量作为 Decoder 的初始状态
        logits = self.fc_out(dec_out)
        return logits

model = ToySeq2Seq()
src_seq = torch.randint(0, 100, (2, 6)) # 2个样本, 长度6
trg_seq = torch.randint(0, 100, (2, 8)) # 2个样本, 长度8
logits = model(src_seq, trg_seq)
print("Seq2Seq 输出 Logits 形状:", logits.shape) # [2, 8, 100]
```

---

## 思考与自测

- **自测 1**：在 Seq2Seq 推理时，贪心搜索（Greedy Search）和束搜索（Beam Search）有什么本质区别？
  > *解析*：贪心搜索每一步仅保留当前概率最高的单一词汇，容易因为一步走错步步走错陷入局部极劣解；束搜索（Beam Search）每一步保留概率排名前 $K$ 条最优质的完整路径（Beam Width 如 $K=4$），在全局生成质量上显著更高。

---

## 关联知识
- [[RNN与门控循环网络]]：传统 Seq2Seq 的循环单元组件。
- [[注意力机制]]：彻底打破 Seq2Seq 固定长度语义瓶颈的关键突破。
- [[Transformer]]：现代全自注意力 Encoder-Decoder 架构巅峰。
