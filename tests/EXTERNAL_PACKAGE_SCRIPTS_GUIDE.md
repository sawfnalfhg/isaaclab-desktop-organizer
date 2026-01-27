# 外部包工具脚本完整指南

## 📋 问题背景

### 为什么官方脚本不能用于外部包？

IsaacLab 的所有官方工具脚本都**只导入主项目环境**（`isaaclab_tasks` 和 `isaaclab_mimic.envs`），**不导入外部包**。这导致：

```python
# 官方脚本的典型导入模式
import isaaclab_mimic.envs  # noqa: F401  # ✅ 主项目 Mimic 环境
import isaaclab_tasks  # noqa: F401       # ✅ 主项目任务
# ❌ 没有 import desktop_organizer（外部包）
```

**结果**：即使外部包已安装并正确注册环境，官方脚本也找不到外部包的环境 ID。

---

## 🔍 受影响的官方脚本

| 脚本路径 | 功能 | 是否导入外部包 | 是否需要修复 |
|---------|------|---------------|------------|
| `scripts/tools/record_demos.py` | 录制遥操作演示 | ❌ | ✅ |
| `scripts/imitation_learning/isaaclab_mimic/annotate_demos.py` | 标注子任务边界 | ❌ | ✅ |
| `scripts/imitation_learning/isaaclab_mimic/generate_dataset.py` | MimicGen 生成数据 | ❌ | ✅ |
| `scripts/imitation_learning/robomimic/train.py` | Behavior Cloning 训练 | ❌ | ✅ |
| `scripts/reinforcement_learning/rsl_rl/train.py` | RL 训练 | ❌ | ✅ |
| `scripts/reinforcement_learning/rsl_rl/play.py` | RL 评估 | ❌ | ✅ |

---

## ✅ 解决方案：外部包专用工具套件

与其逐个修改官方脚本（会在 IsaacLab 升级时被覆盖），我们在**外部包目录**创建完整的工具脚本套件：

```
/root/isaaclab-desktop-organizer/scripts/
├── train_rl.py              ✅ RL 训练（RSL-RL + PPO）
├── play_rl.py               ✅ RL 策略评估
├── record_demos.py          ✅ 录制遥操作演示
├── annotate_demos.py        ✅ 标注子任务边界
├── generate_dataset.py      ✅ MimicGen 数据生成
└── train_bc.py              ✅ Behavior Cloning 训练
```

**关键修改**：所有脚本都添加了：

```python
# ============ CRITICAL: Import external package environments ============
import desktop_organizer  # noqa: F401
# ========================================================================
```

---

## 🚀 完整 Mimic 数据生成流程

### Step 1: 录制人工演示（10 条）

```bash
cd /path/to/IsaacLab

./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --teleop_device keyboard \
  --dataset_file ./datasets/raw.hdf5 \
  --num_demos 10
```

**键盘控制**：
- `WASD` + `QE` + `ZX`：控制末端执行器位置
- `[` / `]`：打开/闭合夹爪
- `ESC`：跳过当前演示
- `Ctrl+C`：停止录制

**验证**：录制完成后应该有 10 条成功的演示，每条演示都完成了抓取 ketchup → 放入 basket 的任务。

---

### Step 2: 手动标注子任务边界

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/annotate_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --input_file ./datasets/raw.hdf5 \
  --output_file ./datasets/annotated.hdf5
```

**交互式标注**：
- `N`：开始播放演示
- `B`：暂停播放
- `S`：标记当前帧为子任务完成点
- `Q`：跳过当前演示

**子任务标注要求**（Desktop Organizer 任务）：
1. **Reach**: 末端执行器接近 ketchup（距离 < 8cm）
2. **Grasp**: 夹爪完全闭合（抓住物体）
3. **Lift**: ketchup 抬升到 0.55m 以上
4. **Place**: ketchup 放入 basket（任务成功）

**注意**：
- 每条演示需要标注 **3 个子任务点**（最后一个 Place 自动由成功判定触发）
- 如果标注不完整，脚本会要求重新标注

---

### Step 3: 使用 MimicGen 生成训练数据

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/generate_dataset.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --input_file ./datasets/annotated.hdf5 \
  --output_file ./datasets/generated.hdf5 \
  --generation_num_trials 100 \
  --num_envs 100 \
  --headless
```

**参数说明**：
- `--generation_num_trials 100`：尝试生成 100 条演示
- `--num_envs 100`：使用 100 个并行环境加速生成
- `--headless`：无头模式（不渲染画面，速度更快）

**预期结果**：
- 从 10 条源演示生成 100 条新演示
- 每条新演示都是在不同的物体位置配置下生成的
- 生成成功率应 > 50%（如果太低，说明随机化范围设置不合理）

**关键配置**（在环境配置中）：
- **Ketchup（目标物体）**：极小范围随机（X: ±1.5cm, Y: ±2cm）
- **干扰物体**：大范围随机（X: 40cm, Y: 45cm）
- **Basket**：小范围随机（X: ±6cm, Y: ±6cm）

---

### Step 4: 添加训练/验证分割标记

```bash
python << 'EOF'
import h5py
import numpy as np

with h5py.File('./datasets/generated.hdf5', 'r+') as f:
    demos = list(f['data'].keys())
    total_demos = len(demos)
    train_count = int(total_demos * 0.8)  # 80% 训练集

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

    print(f"✅ 80% 训练集 ({train_count}), 20% 验证集 ({total_demos - train_count})")
EOF
```

**为什么需要这一步**：
- Robomimic 训练脚本需要数据集包含 `mask` 字段来区分训练集和验证集
- MimicGen 生成的数据集默认不包含这些字段

---

### Step 5: 训练 Behavior Cloning 策略

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_bc.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --algo bc \
  --dataset ./datasets/generated.hdf5 \
  --epochs 200
```

**训练参数**：
- `--algo bc`：Behavior Cloning 算法
- `--epochs 200`：训练 200 轮（可根据验证集表现调整）
- 默认保存路径：`./logs/robomimic/Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0/`

**监控训练**：
```bash
# 使用 TensorBoard 监控
cd /path/to/IsaacLab
source .venv/bin/activate
tensorboard --logdir=logs/robomimic --port=6006
```

**关键指标**：
- `Train_Loss`：训练损失（应持续下降）
- `Rollout_Success_Rate`：验证集成功率（目标 > 70%）

---

## 📊 与官方脚本的对比

### 方案 1：修改官方脚本 ❌ 不推荐

```bash
# 修改 IsaacLab 源码
vim scripts/tools/record_demos.py
# 手动添加: import desktop_organizer

# 缺点:
# - 修改 IsaacLab 源码（升级时会丢失）
# - 每个脚本都要手动修改
# - 不符合外部包的独立性原则
```

### 方案 2：使用外部包专用脚本 ✅ 推荐

```bash
# 使用外部包自带脚本，无需修改 IsaacLab
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  ...

# 优点:
# - 不修改 IsaacLab 源码
# - 升级 IsaacLab 不受影响
# - 所有工具脚本集中管理
# - 命令行参数与官方完全一致
```

---

## 🎯 命令对照表

| 官方脚本路径 | 外部包脚本路径 | 功能 |
|------------|--------------|------|
| `scripts/tools/record_demos.py` | `/root/isaaclab-desktop-organizer/scripts/record_demos.py` | 录制演示 |
| `scripts/imitation_learning/isaaclab_mimic/annotate_demos.py` | `/root/isaaclab-desktop-organizer/scripts/annotate_demos.py` | 标注子任务 |
| `scripts/imitation_learning/isaaclab_mimic/generate_dataset.py` | `/root/isaaclab-desktop-organizer/scripts/generate_dataset.py` | 生成数据 |
| `scripts/imitation_learning/robomimic/train.py` | `/root/isaaclab-desktop-organizer/scripts/train_bc.py` | BC 训练 |
| `scripts/reinforcement_learning/rsl_rl/train.py` | `/root/isaaclab-desktop-organizer/scripts/train_rl.py` | RL 训练 |
| `scripts/reinforcement_learning/rsl_rl/play.py` | `/root/isaaclab-desktop-organizer/scripts/play_rl.py` | RL 评估 |

**使用原则**：
- ✅ **外部包环境**：使用 `/root/isaaclab-desktop-organizer/scripts/` 下的脚本
- ✅ **主项目环境**：使用官方 `scripts/` 下的脚本

---

## ❓ 常见问题

### Q1: 为什么我的主机上用官方脚本可以，换了主机就不行？

**答**：你的第一个主机上有**主项目代码**，主项目的 `desktop_organizer/__init__.py` 调用了 `import_packages(__name__)`，会自动导入 `mimic/` 子模块，巧合注册了和外部包同名的环境 `Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0`。

- 第一个主机：官方脚本 → 导入主项目 → 自动导入 mimic/ → 注册环境（**主项目版本**）✅
- 第二个主机：官方脚本 → 导入主项目（不存在）→ 找不到环境 ❌

### Q2: 外部包脚本和官方脚本的命令行参数一样吗？

**答**：**完全一样**！外部包脚本是基于官方脚本创建的，只是添加了 `import desktop_organizer`，其他内容完全相同。

### Q3: 如果 IsaacLab 升级了，外部包脚本还能用吗？

**答**：**大概率可以**。如果 IsaacLab 更新了脚本接口，你只需：
1. 从新版 IsaacLab 复制官方脚本到外部包
2. 添加 `import desktop_organizer` 这一行
3. 测试验证

这比每次都修改官方脚本方便得多。

### Q4: 能否让官方脚本自动识别外部包？

**答**：理论上可以，但需要修改 IsaacLab 的核心导入逻辑，不推荐。**使用外部包专用脚本是最佳实践**。

### Q5: 我应该把外部包脚本提交到 Git 吗？

**答**：**应该**！外部包脚本是你项目的一部分，应该和环境配置、资产文件一起提交到版本控制。这样：
- 其他人克隆你的项目后可以直接使用
- 记录了脚本的修改历史
- 方便团队协作

---

## 🔧 故障排查

### 错误 1: "Environment 'Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0' doesn't exist"

**症状**：
```bash
./isaaclab.sh -p scripts/tools/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0
# gymnasium.error.NameNotFound: Environment 'Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0' doesn't exist.
```

**原因**：使用了官方脚本，没有导入外部包

**解决**：
```bash
# 改用外部包脚本
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0
```

---

### 错误 2: "ModuleNotFoundError: No module named 'desktop_organizer'"

**症状**：
```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0
# ModuleNotFoundError: No module named 'desktop_organizer'
```

**原因**：外部包未安装或未激活正确的环境

**解决**：
```bash
# 1. 确认在 IsaacLab 环境中
cd /path/to/IsaacLab
source .venv/bin/activate

# 2. 重新安装外部包
cd /root/isaaclab-desktop-organizer
pip install -e ".[bc]"  # 安装 BC 依赖

# 3. 验证
python -c "import desktop_organizer; print('✅ 安装成功')"
```

---

### 错误 3: MimicGen 生成成功率 0%

**症状**：
```
Generation stats:
  Environments: 100
  Attempts: 100
  Success: 0 (0.0%)
```

**原因**：随机化范围设置不合理，目标物体位置变化太大

**解决**：
1. 检查环境配置中的 `per_object_pose_ranges`
2. 确保目标物体（ketchup）范围 ≤ ±2cm
3. 用脚本分析源数据的实际位置分布：
```python
import h5py
import numpy as np

with h5py.File('./datasets/annotated.hdf5', 'r') as f:
    ketchup_positions = []
    for demo_name in f['data'].keys():
        obs = f[f'data/{demo_name}/obs']
        ketchup_pos = np.array(obs['ketchup_pos'])
        ketchup_positions.append(ketchup_pos)

    all_pos = np.concatenate(ketchup_positions, axis=0)
    print(f"X: min={all_pos[:, 0].min():.4f}, max={all_pos[:, 0].max():.4f}")
    print(f"Y: min={all_pos[:, 1].min():.4f}, max={all_pos[:, 1].max():.4f}")
    print(f"Z: min={all_pos[:, 2].min():.4f}, max={all_pos[:, 2].max():.4f}")
```

---

## 📚 相关文档

- [外部包训练脚本修复记录](/root/isaaclab-desktop-organizer/tests/EXTERNAL_PACKAGE_FIXES.md) - train_rl.py 的 6 个关键修复
- [外部包 README](/root/isaaclab-desktop-organizer/README.md) - 完整的安装和使用指南
- [IsaacLab Mimic 官方教程](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/05_imitation_learning/mimic_usage.html)
- [Robomimic 官方文档](https://robomimic.github.io/)

---

## ✅ 最佳实践总结

1. **外部包环境 → 使用外部包脚本**
   - 所有脚本位于 `/root/isaaclab-desktop-organizer/scripts/`
   - 不需要修改 IsaacLab 源码

2. **主项目环境 → 使用官方脚本**
   - 所有脚本位于 `scripts/`
   - IsaacLab 自动导入主项目环境

3. **命令行参数完全相同**
   - 外部包脚本与官方脚本的参数一致
   - 只需替换脚本路径即可

4. **工具脚本纳入版本控制**
   - 提交到 Git，方便团队协作
   - 记录修改历史

5. **IsaacLab 升级时**
   - 复制新版官方脚本到外部包
   - 添加 `import desktop_organizer` 一行
   - 测试验证即可

---

**🎉 完成！现在你可以在任何主机上使用外部包的完整 Mimic 工具链了！**
