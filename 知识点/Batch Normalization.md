# 批归一化（Batch Normalization, BN）

> 掌握度：🟡 接触过 ｜ 所属模块：泛化、调优与评估

## 一句话直觉
批归一化是网络内部的**“各级安检站与交通秩序员”**：随着网络层数加深，中间层激活值的分布会随着前层参数更新而不断漂移变形（内部协变量偏移）；BN 在每一层强制将当前 Batch 的数据重新“拉回”到均值为 0、方差为 1 的标准状态，并赋予两个可学习的“微调旋钮”（$\gamma$ 缩放与 $\beta$ 平移），彻底治愈深层网络的梯度消失与梯度爆炸。

---

## 核心要点与数学公式

### 1. 批归一化 4 步标准数学算法

针对当前 Mini-Batch $\mathcal{B} = \{x_1, \dots, x_m\}$：

1. **计算 Mini-Batch 均值**：
   $$\mu_\mathcal{B} = \frac{1}{m} \sum_{i=1}^m x_i$$
2. **计算 Mini-Batch 方差**：
   $$\sigma_\mathcal{B}^2 = \frac{1}{m} \sum_{i=1}^m (x_i - \mu_\mathcal{B})^2$$
3. **标准化（Standardization）**：
   $$\hat{x}_i = \frac{x_i - \mu_\mathcal{B}}{\sqrt{\sigma_\mathcal{B}^2 + \epsilon}}$$
4. **尺度缩放与平移变换（Scale and Shift）**：
   $$y_i = \gamma \hat{x}_i + \beta$$
   - $\gamma$（缩放因子）和 $\beta$（平移偏置）是**随网络一同反向传播学习的参数**，若网络觉得不需要归一化，可自行学出 $\gamma = \sigma, \beta = \mu$ 恢复原貌！

---

### 2. 训练阶段 vs 推理阶段的关键差异

- **训练阶段（`model.train()`）**：
  - 使用当前 Batch 的实时均值 $\mu_\mathcal{B}$ 和方差 $\sigma_\mathcal{B}^2$；
  - 维护全局滑动平均（Running Mean / Running Var）：
    $$\mu_{\text{running}} = (1 - \text{momentum}) \cdot \mu_{\text{running}} + \text{momentum} \cdot \mu_\mathcal{B}$$
- **推理/部署阶段（`model.eval()`）**：
  - **彻底冻结 Batch 统计**！直接使用预先缓存好的全局 $\mu_{\text{running}}$ 和 $\sigma_{\text{running}}^2$。

---

## 最小验证代码（NumPy 手写单层 BN）

```python
import numpy as np

# 1. 模拟一个 Mini-Batch 的特征 [Batch=4, Channels=2]
x = np.array([[10.0, 2.0],
              [12.0, 4.0],
              [8.0, 1.0],
              [14.0, 5.0]])

gamma = np.array([1.0, 1.0])
beta = np.array([0.0, 0.0])
eps = 1e-5

# 2. 前向计算
mean = np.mean(x, axis=0)
var = np.var(x, axis=0)

x_hat = (x - mean) / np.sqrt(var + eps)
out = gamma * x_hat + beta

print("原始均值与方差:", mean, var)
print("BN 输出后均值 (期望0):", np.mean(out, axis=0).round(4))
print("BN 输出后方差 (期望1):", np.var(out, axis=0).round(4))
```

---

## 工程与业务映射

- **🚨 嵌入式/RKNN 部署神器：Conv + BN 算子融合（Operator Fusion）**：
  - 在推理阶段，BN 的数学公式本质就是一个纯线性变换：$y = \frac{\gamma}{\sigma}(Wx + b - \mu) + \beta$；
  - 因此，在导出 ONNX / RKNN 量化时，**BN 层会被直接数学合并吸收到前一层的卷积权重 $W$ 和偏置 $b$ 中**！
  - **结果**：推理时 BN 算子耗时直接变为 **0 毫秒**，完全不占 NPU 芯片算力！
- **卷积层放置位置**：通常按照 `Conv -> BatchNorm -> ReLU` 的顺序组合。

---

## 思考与自测

- **自测 1**：如果训练时的 Batch Size 设置得非常小（例如 Batch Size = 1 或 2），为什么 Batch Normalization 的性能会急剧崩盘？
  > *解析*：Batch Size 过小时，单批次的均值和方差具有极大的随机误差（统计不可靠），导致归一化引入过多破坏性噪声；且滑动平均难以收敛。此时应采用 **Group Normalization (GN)** 或 **Layer Normalization (LN)**。

---

## 关联知识
- [[数据预处理与归一化]]：输入层归一化 vs 中间层批归一化。
- [[模型部署基础（ONNX与量化）]]：Conv-BN 融合在嵌入式端侧的实现。
- [[经典网络]]：ResNet 等深层卷积网络能训成功的核心支柱。
