# 经典网络：LeNet → AlexNet → VGG → ResNet

> 掌握度：🟡 接触过 ｜ 所属：四、卷积神经网络（CNN） ｜ 更新：2026-08-14

## 一句话直觉
从手写数字的开山鼻祖（LeNet-5），到点燃深度学习革命火种的开山重器（AlexNet），再到整齐美观的模块化堆叠（VGG），最后到用一条**“残差捷径（Skip Connection）”彻底打破网络深度诅咒的封神之作（ResNet）**。

## 核心要点与数学公式
- **ResNet 残差核心公式**：
  $$y = \mathcal{F}(x, \{W_i\}) + x$$
  $$\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \left( \frac{\partial \mathcal{F}}{\partial x} + 1 \right)$$
  右侧常数项 $+1$ 确保梯度毫无阻碍无损直达浅层。

## 最小验证代码（<20行纯 PyTorch）
```python
import torch
import torch.nn as nn
class ResBlock(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.net = nn.Sequential(nn.Conv2d(c,c,3,1,1), nn.BatchNorm2d(c), nn.ReLU(), nn.Conv2d(c,c,3,1,1), nn.BatchNorm2d(c))
    def forward(self, x): return torch.relu(self.net(x) + x)
```

## 工程与业务映射
- **androidhub / YOLO / RKNN**：ResNet / CSP 残差主干网是视觉目标检测的核心特征提取器。

## 思考与自测
- **自测 1**：退化问题（Degradation）和过拟合的区别？
  > *解析*：退化问题是“深层网络在训练集上的误差反而比浅层更高（学不会）”；ResNet 让深层网络至少不劣于浅层（恒等映射）。

## 关联知识
- [[卷积层与池化层]]
- [[目标检测（YOLO 系列）]]
