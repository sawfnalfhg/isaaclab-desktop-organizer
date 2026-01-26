# 📘 MimicGen 数据生成完全指南

## 🎯 MimicGen 是什么？

**MimicGen** 是一个数据增强工具，用于从少量人工演示生成大量高质量的训练数据。

### 核心思想

```
10 条人工演示  →  MimicGen  →  100+ 条合成演示
```

**原理**：
1. 把演示轨迹分解成多个子任务片段（Reach, Grasp, Lift, Place）
2. 通过随机化物体位置，组合不同源演示的子任务片段
3. 生成新的、符合物理规律的演示轨迹

---

## 📂 完整数据流程

### Step 1: 录制人工演示（源数据）

```bash
cd /root/IsaacLab

# 用键盘遥操作录制 10 条演示
./isaaclab.sh -p scripts/tools/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --teleop_device keyboard \
  --dataset_file ./datasets/desktop_organizer_raw.hdf5 \
  --num_demos 10
```

**键盘控制**（根据任务可能不同）：
- `WASD` - 移动末端执行器（XY 平面）
- `Q/E` - 上升/下降
- `Space` - 切换夹爪开/关
- `R` - 重置环境
- `Esc` - 保存并退出

**输出**：`./datasets/desktop_organizer_raw.hdf5`（10 条演示，每条 200-300 帧）

---

### Step 2: 标注子任务边界

```bash
python scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
  --dataset ./datasets/desktop_organizer_raw.hdf5 \
  --output ./datasets/desktop_organizer_annotated.hdf5
```

**标注内容**（4 个子任务）：
- **Reach**: 末端执行器接近 ketchup 的帧号（例如：第 50 帧）
- **Grasp**: 夹爪闭合完成的帧号（例如：第 80 帧）
- **Lift**: ketchup 抬升到足够高度的帧号（例如：第 120 帧）
- **Place**: ketchup 进入 basket 的帧号（例如：第 200 帧，任务结束）

**工具界面**：
- 显示演示视频
- 可以前进/后退帧
- 点击按钮标记子任务完成时间点

**输出**：`./datasets/desktop_organizer_annotated.hdf5`（带子任务边界的 10 条演示）

---

### Step 3: 生成大量合成数据（MimicGen）

```bash
python scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --input_file ./datasets/desktop_organizer_annotated.hdf5 \
  --output_file ./datasets/generated_dataset.hdf5 \
  --generation_num_trials 100 \
  --num_envs 100 \
  --headless
```

**重要参数**：

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `--task` | 环境名称 | `Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0` |
| `--input_file` | 带标注的源数据 | 上一步的输出文件 |
| `--output_file` | 生成的数据集 | `./datasets/generated_dataset.hdf5` |
| `--generation_num_trials` | 尝试生成的数量 | 100（会生成更多或更少，取决于成功率） |
| `--num_envs` | 并行环境数 | 100（越多越快） |
| `--headless` | 无 GUI 运行 | 加速生成 |

**内部工作流程**：

1. **随机化场景**：改变 ketchup、basket、干扰物体的位置
2. **选择源片段**：从 10 条源演示中，为每个子任务选择最接近的片段
3. **插值和执行**：
   - 插值到子任务起始姿态
   - 执行子任务动作（加噪声）
   - 重复 4 个子任务
4. **成功判定**：检查 ketchup 是否成功放入 basket
5. **保存数据**：成功的轨迹保存到 HDF5 文件

**输出**：`./datasets/generated_dataset.hdf5`（80-120 条成功演示，取决于随机性）

**生成日志示例**：
```
[INFO] Loaded 10 source demos from dataset
[INFO] Starting generation with 100 parallel environments...
[INFO] Generated 85 successful demos out of 100 trials (85% success rate)
[INFO] Saved to ./datasets/generated_dataset.hdf5
```

---

### Step 4: 添加训练/验证分割

Robomimic 训练需要在数据集中标记哪些是训练集、哪些是验证集：

```bash
python << 'EOF'
import h5py
import numpy as np

with h5py.File('./datasets/generated_dataset.hdf5', 'r+') as f:
    demos = list(f['data'].keys())
    total_demos = len(demos)
    train_count = int(total_demos * 0.8)  # 80% 训练

    # 为每个 demo 添加 mask 字段
    for i, demo_name in enumerate(demos):
        demo = f[f'data/{demo_name}']
        if 'mask' in demo:
            continue
        mask_data = np.array([1 if i < train_count else 0], dtype=np.int8)
        demo.create_dataset('mask', data=mask_data)

    # 创建 filter keys
    if 'mask' not in f:
        f.create_group('mask')

    train_demos = [d.encode('utf-8') for d in demos[:train_count]]
    valid_demos = [d.encode('utf-8') for d in demos[train_count:]]

    if 'train' in f['mask']:
        del f['mask/train']
    if 'valid' in f['mask']:
        del f['mask/valid']

    f.create_dataset('mask/train', data=np.array(train_demos, dtype='S'))
    f.create_dataset('mask/valid', data=np.array(valid_demos, dtype='S'))

    print(f"✅ 训练集: {train_count}, 验证集: {total_demos - train_count}")
EOF
```

---

### Step 5: 训练 BC 策略

```bash
./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0 \
  --algo bc \
  --dataset ./datasets/generated_dataset.hdf5 \
  --epochs 200
```

**训练配置**（在你的 `bc.json` 中）：
- 网络：2 层 MLP，每层 1024 神经元
- 学习率：1e-4
- Batch size：100
- 优化器：Adam

**输出**：
- 训练日志：`./logs/robomimic/`
- 模型检查点：每 50 epochs 保存一次
- TensorBoard 日志

---

## 🔧 MimicGen 配置（在环境中定义）

**注意**：新版 IsaacLab 不使用独立的配置文件，而是在 **Mimic 环境配置** 中定义。

配置位置：`desktop_organizer/envs/mimic_env_cfg.py`

### 关键配置项

```python
@configclass
class FrankaDesktopOrganizerIKRelMimicEnvCfg(FrankaDesktopOrganizerIKRelEnvCfg, MimicEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # 数据生成配置
        self.datagen_config.generation_guarantee = True          # 保证生成数量
        self.datagen_config.generation_num_trials = 10           # 每个源演示尝试 10 次
        self.datagen_config.generation_select_src_per_subtask = True  # 每个子任务独立选择源
        self.datagen_config.max_num_failures = 25                # 最大失败次数

        # 子任务配置（4 个子任务）
        subtask_configs = []

        # 子任务 1: Reach
        subtask_configs.append(
            SubTaskConfig(
                object_ref="ketchup",                    # 参考物体
                subtask_term_signal="reach",             # 终止信号名称
                subtask_term_offset_range=(3, 8),        # 边界偏移范围（帧）
                selection_strategy="nearest_neighbor_object",  # 选择策略
                action_noise=0.03,                       # 动作噪声
                num_interpolation_steps=5,               # 插值步数
            )
        )

        # 子任务 2-4: Grasp, Lift, Place
        # ... 类似配置
```

### 配置参数详解

| 参数 | 说明 | 推荐值 | 影响 |
|------|------|--------|------|
| **generation_guarantee** | 保证生成指定数量的演示 | True | 失败时自动重试 |
| **generation_num_trials** | 每个源演示尝试生成次数 | 10 | 总生成数 = 源数 × trials |
| **max_num_failures** | 最大连续失败次数 | 25 | 避免无限循环 |
| **subtask_term_offset_range** | 子任务边界偏移（帧） | (3, 8) | 增加轨迹多样性 |
| **action_noise** | 执行时的动作噪声 | 0.03 | 增加鲁棒性 |
| **num_interpolation_steps** | 子任务间插值步数 | 5 | 平滑轨迹连接 |
| **selection_strategy** | 源片段选择策略 | `nearest_neighbor_object` | 选择最相似的源 |

---

## 📊 数据量建议

| 场景 | 源演示 | 生成目标 | 训练轮数 | 预期性能 | 时间估算 |
|------|--------|---------|---------|---------|---------|
| **快速测试** | 10 | 50 | 50 | 基础功能验证 | 20 分钟 |
| **正常训练** | 10 | 100 | 200 | 中等性能（75%） | 1 小时 |
| **充分训练** | 20 | 200 | 300 | 较好性能（80%+） | 2-3 小时 |
| **高质量训练** | 50 | 500 | 500 | 最佳性能（85%+） | 5-6 小时 |

---

## ⚠️ 常见问题

### 1. 生成成功率低（< 30%）

**原因**：随机范围太大，目标物体位置变化超出源数据分布

**解决**：
- 分析源数据中 ketchup 的实际位置范围
- 缩小 `randomize_ketchup` 的 `pose_range`（从 ±50cm 缩小到 ±5cm）
- 增加源演示的多样性（不同起始位置）

### 2. 子任务边界冲突

**原因**：`subtask_term_offset_range` 太大，导致相邻子任务重叠

**解决**：
- 缩小偏移范围：从 `(10, 20)` 缩小到 `(3, 8)`
- 检查标注的子任务边界是否准确

### 3. 数据集缺少 mask 字段

**原因**：Mimic 生成的数据集没有训练/验证分割标记

**解决**：运行 Step 4 中的脚本添加 mask

### 4. 训练时找不到 observation keys

**原因**：BC 配置文件中的 observation keys 和数据集不匹配

**解决**：
- 检查 `bc.json` 中的 `observation.modalities.obs.low_dim`
- 确保与数据集中的 keys 完全一致（如 `ketchup_pos` 而不是 `object_position`）

---

## 🎓 关键经验

1. **源数据质量 > 数量**：10 条高质量的演示胜过 50 条糟糕的演示
2. **目标物体位置要稳定**：随机范围控制在 ±2-5cm，才能成功匹配轨迹
3. **子任务标注要准确**：边界标注错误会导致生成失败
4. **干扰物体可以大范围随机**：orange_juice 和 cream_cheese 随机范围 ±30cm
5. **检查成功率**：生成成功率应 > 70%，否则调整随机范围

---

## 📚 相关文档

- [MimicGen 论文](https://arxiv.org/abs/2310.17596)
- [Robomimic 文档](https://robomimic.github.io/)
- [Isaac Lab Mimic 教程](https://isaac-sim.github.io/IsaacLab/source/tutorials/05_imitation_learning/mimic.html)

---

**🎉 现在你应该完全理解 MimicGen 的工作原理了！**
