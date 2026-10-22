# 目标检测（YOLO 系列与核心机制）

> 掌握度：🟡 接触过 ｜ 所属模块：卷积神经网络（CNN）

## 一句话直觉
目标检测是给图像打上**“定位框（Where）+ 类别标签（What）”**的双重任务。相比于先提候选区域再逐个分类的慢速两阶段算法（Faster R-CNN），YOLO（You Only Look Once）就像**“神枪手一眼扫过全图”**：将整张图片网格化，单次前向推理直接端到端同时预测所有物体的坐标边界框和分类得分，实现工业级实时高帧率检测。

---

## 核心要点与数学公式

### 1. YOLO 经典三段式架构（Backbone - Neck - Head）

```
输入图像 (640x640x3)
   │
   ▼
【1. Backbone (主干提取网)】: CSPDarknet / C2f ──▶ 提取多尺度特征 (P3 小目标, P4 中目标, P5 大目标)
   │
   ▼
【2. Neck (多尺度融合网)】: FPN (自顶向下传递语义) + PAN (自底向上传递定位细节)
   │
   ▼
【3. Head (解耦检测头)】: 分类分支 (Class Logits) + 回归分支 (Bounding Box 坐标偏移)
   │
   ▼
【4. 后处理 NMS】: 非极大值抑制消除冗余重叠预测框
```

---

### 2. 边界框回归损失（IoU 演进）

- **IoU（Intersection over Union / 交并比）**：
  $$\text{IoU} = \frac{\text{Area}(B \cap B^{gt})}{\text{Area}(B \cup B^{gt})}$$
- **CIoU Loss（Complete IoU / YOLOv5~v8 标配）**：
  综合惩罚**重叠面积**、**中心点欧氏距离**与**宽高长宽比一致性**：
  $$\mathcal{L}_{CIoU} = 1 - \text{IoU} + \frac{\rho^2(b, b^{gt})}{c^2} + \alpha v$$

---

### 3. NMS（Non-Maximum Suppression / 非极大值抑制）

1. 按照分类置信度从高到低对所有预测框排序；
2. 选出当前最高分的框 $B_{max}$ 保留并移入输出列表；
3. 计算剩余所有框与 $B_{max}$ 的 IoU，若 $\text{IoU} > \text{Threshold}$（如 0.45），则直接**抑制/丢弃**；
4. 重复上述步骤直到候选框列表为空。

---

## 最小验证代码（NumPy 手写非极大值抑制 NMS）

```python
import numpy as np

def nms(boxes, scores, iou_threshold=0.5):
    # boxes 形状: [N, 4] -> (x1, y1, x2, y2)
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1] # 按置信度降序排序
    
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        if order.size == 1:
            break
        
        # 计算当前最高分框与其他所有框的交集
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        
        # IoU 计算
        iou = inter / (areas[i] + areas[order[1:]] - inter)
        
        # 保留 IoU 小于阈值的框
        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]
        
    return keep

# 模拟 3 个高度重叠的检测框
boxes = np.array([[50, 50, 100, 100], [52, 53, 102, 101], [200, 200, 300, 300]])
scores = np.array([0.92, 0.75, 0.88])

survived = nms(boxes, scores, iou_threshold=0.5)
print("NMS 保留的检测框索引:", survived) # 输出 [0, 2] 成功过滤掉 1 号重叠框
```

---

## 工程与业务映射

- **端侧部署优化（androidhub / RKNN 移植）**：
  - **Anchor-Free 解耦头**：YOLOv8 摒弃了复杂的 Anchor 匹配，模型结构更精简；
  - **后处理 NMS C++ 实现**：NPU 处理前向推理（产出 `[1, 84, 8400]` 输出张量），CPU 使用 SIMD 或 OpenMP 执行高效 NMS 与坐标映射，保持 30+ FPS 实时渲染。

---

## 思考与自测

- **自测 1**：在 YOLO 中，特征金字塔（FPN + PAN）为什么要设计 3 个不同尺度的输出层（P3, P4, P5）？
  > *解析*：小物体在深层网络中下采样 32 倍后像素信息几乎丢失，因此利用浅层（P3，下采样 8 倍，感受野小、细节丰富）检测小目标；中层（P4）检测中等目标；深层（P5，下采样 32 倍，感受野大、语义丰富）检测大目标。

---

## 关联知识
- [[卷积层与池化层]]：YOLO 的基础特征提取积木。
- [[模型评估指标]]：目标检测核心评估指标 mAP@0.5 与 IoU。
- [[模型部署基础（ONNX与量化）]]：YOLO 导出 ONNX 及 INT8 量化部署在 RKNN NPU 上的完整流程。
