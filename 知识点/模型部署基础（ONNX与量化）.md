# 模型部署基础（ONNX 导出与 INT8 量化 / RKNN）

> 掌握度：🟡 接触过 ｜ 所属模块：工程实践

## 一句话直觉
模型训练是**“在实验室里烧高规格显卡锻造精密仪器”**；而模型部署则是**“将重型仪器瘦身压缩、脱水烘干为能在边缘芯片（手机、AndroidHub、瑞芯微 NPU）上毫秒级运转的高效便携机”**。ONNX 是跨框架的**“通用世界语”**，而 INT8 量化则是将 32 位浮点数精准压缩为 8 位整数，以 $1/4$ 的内存体积和功耗实现数倍的算力爆发。

---

## 核心要点与数学公式

### 1. 跨平台标准协议：ONNX（Open Neural Network Exchange）
- **核心定位**：打通训练框架（PyTorch/TensorFlow）与推理引擎（TensorRT / ONNXRuntime / RKNN / OpenVINO / TFLite）的中间静态计算图格式。
- **导出关键**：固定动态 Shape、算子集版本（`opset_version=12`）、去除仅训练算子（Dropout/BatchNorm 参数折叠）。

---

### 2. INT8 量化数学原理（Quantization）

将连续的 32 位浮点范围 $[x_{min}, x_{max}]$ 线性映射到 $[-128, 127]$（有符号）或 $[0, 255]$（无符号）：

$$q = \text{round}\left( \frac{x}{S} \right) + Z$$

- **缩放因子 $S$（Scale）**：$S = \frac{x_{max} - x_{min}}{q_{max} - q_{min}}$
- **零点偏移 $Z$（Zero Point）**：浮点 0 对应的整数值（对称量化时 $Z=0$）。
- **反量化（Dequantization）**：$\tilde{x} = S \cdot (q - Z)$

---

### 3. PTQ（训练后量化）vs QAT（量化感知训练）

| 模式 | 流程与实现机制 | 优点 | 缺点 |
| :--- | :--- | :--- | :--- |
| **PTQ (Post-Training Quantization)** | 使用少量无标签真实图片（100~500张）作为**校准集（Calibration）**，统计每层激活值的浮点极值直方图直接确定 Scale $S$ | 几分钟搞定，无需重新训练 | 敏感模型（如 YOLO 小目标）精度可能轻微掉点 |
| **QAT (Quantization-Aware Training)** | 在 PyTorch 训练过程中插入 FakeQuantize 伪量化节点，前向模拟 8 位截断误差，反向传播 Straight-Through Estimator (STE) 微调权重 | 精度近乎 100% 无损 | 需要完整的训练代码与训练数据集微调几轮 |

---

## 最小验证代码（PyTorch 导出 ONNX 与检查）

```python
import torch
import torch.nn as nn

# 1. 定义一个简单的视觉分类器
class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.fc = nn.Linear(16 * 32 * 32, 10)
    def forward(self, x):
        return self.fc(self.relu(self.conv(x)).flatten(1))

model = SimpleNet().eval()
dummy_input = torch.randn(1, 3, 32, 32)

# 2. 导出为 ONNX
torch.onnx.export(
    model,
    dummy_input,
    "simple_model.onnx",
    input_names=["input"],
    output_names=["output"],
    opset_version=12,
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)
print("ONNX 模型导出成功: simple_model.onnx")
```

---

## 工程与业务映射（androidhub / RKNN 最佳实践）

```
PyTorch (.pt) ──▶ ONNX (.onnx) ──▶ RKNN-Toolkit2 (量化校准) ──▶ RKNN 权重 (.rknn) ──▶ Android / C++ NPU 推理
```
- **RKNN 量化避坑要点**：
  1. **校准集必须真实覆盖典型场景**（暗光、逆光、各尺度目标）；
  2. **均值方差归一化（Mean/Std）** 必须在 RKNN 配置文件（`dataset.txt` / `config`）中指定，让 NPU 硬件底层自动完成图像预处理，省去 CPU 图像拷贝开销。

---

## 思考与自测

- **自测 1**：为什么 INT8 量化能让模型在边缘端芯片上的推理速度大幅提升数倍？
  > *解析*：
  > 1. **内存带宽瓶颈缓解**：权重体积缩小 75%，内存读取吞吐量大幅降低；
  > 2. **硬件算力密度翻倍**：NPU 芯片内部的整数 INT8 MAC 计算单元面积远小于 FP32 浮点单元，同等硅片面积下可塞入 4~8 倍的 INT8 并行计算核心。

---

## 关联知识
- [[目标检测（YOLO 系列）]]：YOLO 模型在端侧部署的标准流程。
- [[Batch Normalization]]：Conv + BN 算子融合在 ONNX/RKNN 转换中的自动化执行。
- [[PyTorch基础]]：PyTorch 动态图到 ONNX 静态图的转换。
