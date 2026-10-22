# PyTorch 基础（张量操作、自动求导与核心模式）

> 掌握度：🟡 接触过 ｜ 所属模块：工程实践

## 一句话直觉
PyTorch 是现代深度学习的**“Pythonic 瑞士军刀”**：它完美继承了 NumPy 简洁自然的张量语法，同时赋予了两大超能力——**GPU 显卡上万倍的并行硬件加速**与**动态自动求导引擎（Autograd）**，让开发者可以像写原生 Python 代码一样自由构建任意复杂的神经网络。

---

## 核心要点与数学公式

### 1. PyTorch 经典四步训练闭环范式（Standard Training Loop）

```python
# 黄金四步训练死记硬背模版:
1. optimizer.zero_grad()  # 清空历史梯度 (防止梯度累加)
2. outputs = model(inputs) # 1. 前向传播计算预测
3. loss = criterion(outputs, labels) # 2. 损失函数打分
4. loss.backward()        # 3. 反向传播自动计算梯度
5. optimizer.step()       # 4. 优化器更新参数
```

---

### 2. 张量设备迁移与内存管理

- **CPU $\to$ GPU 迁移**：
  ```python
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  model = model.to(device)
  inputs, labels = inputs.to(device), labels.to(device)
  ```
- **脱离计算图与 NumPy 互转**：
  - `tensor.detach().cpu().numpy()`：先从动态计算图中剥离、搬回 CPU 内存、再转为 NumPy 数组。

---

## 最小验证代码（PyTorch 端到端线性回归）

```python
import torch
import torch.nn as nn

# 1. 构造真实关系: y = 2*x + 1 + 噪声
x = torch.randn(100, 1)
y = 2 * x + 1 + torch.randn(100, 1) * 0.1

# 2. 定义单层线性模型与优化器
model = nn.Linear(1, 1)
criterion = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

# 3. 训练 50 轮
for epoch in range(50):
    optimizer.zero_grad()
    loss = criterion(model(x), y)
    loss.backward()
    optimizer.step()

# 4. 检查学习到的权重与偏置 (期望 w≈2, b≈1)
w_learned = model.weight.item()
b_learned = model.bias.item()
print(f"学到的参数: w = {w_learned:.4f} (期望 2.0) | b = {b_learned:.4f} (期望 1.0)")
```

---

## 工程与业务映射

- **PyTorch 与 ONNX / RKNN 的衔接**：
  - `torch.onnx.export(model, dummy_input, "model.onnx", opset_version=12)` 是将 PyTorch 算法交付给 Android / 嵌入式开发者的标准工程分界线。

---

## 思考与自测

- **自测 1**：在执行模型推理测试时，为什么要使用 `with torch.no_grad():` 上下文管理器？
  > *解析*：禁用 Autograd 计算图构建，避免在前向过程中在显存中缓存任何中间激活张量（Activation Tensors），显著降低显存开销 70% 以上，并提速推理速度。

---

## 关联知识
- [[计算图与自动微分]]：PyTorch 核心求导引擎 Autograd。
- [[模型部署基础（ONNX与量化）]]：模型从 PyTorch 导出到边缘端部署。
