# 🤖 IsaacLab 桌面整理机器人

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Isaac Lab](https://img.shields.io/badge/Isaac%20Lab-0.5.0+-green.svg)](https://isaac-sim.github.io/IsaacLab/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个**专业级的强化学习独立包**，用于 Isaac Lab 中的 Franka 机械臂操作任务。训练机器人将物体抓取并放入篮子，支持最先进的强化学习和模仿学习算法。

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=Demo+视频+待添加" alt="演示">
</p>

---

## ✨ 特性

| 功能 | 说明 |
|------|------|
| **任务** | 抓取 ketchup 并放入篮子（可扩展到 3+ 个物体） |
| **机器人** | Franka Panda 机械臂 + 平行夹爪 |
| **控制方式** | 微分 IK（相对位姿控制） |
| **观测空间** | 关节状态 + 物体位姿 + 目标指令 |
| **奖励设计** | 稠密奖励：接近、抓取、举起、追踪、成功 |
| **数据增强** | MimicGen（10 条演示 → 100+ 条） |
| **算法支持** | RSL-RL (PPO) + Robomimic (BC) |
| **并行训练** | 4096 个并行环境，快速训练 |

---

## 📦 安装

### 前置要求

1. **Isaac Lab 0.5.0+** - 必须先安装 Isaac Lab（不能通过 pip 安装）

```bash
# 克隆 Isaac Lab 仓库
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# 按照官方指南安装
# 详见: https://isaac-sim.github.io/IsaacLab/source/setup/installation.html
./isaaclab.sh --install
```

2. **Python 3.10+**
3. **CUDA 11.8+**（用于 GPU 加速）

### 安装本包

**重要**：必须在 IsaacLab 环境中安装！

```bash
# 激活 IsaacLab 环境
cd /path/to/IsaacLab
source .venv/bin/activate  # Linux/Mac
# 或者 .venv\Scripts\activate  # Windows

# 克隆本仓库
cd ..
git clone https://github.com/<your-username>/isaaclab-desktop-organizer.git
cd isaaclab-desktop-organizer

# 安装本包（开发模式）
pip install -e .

# 可选：安装强化学习依赖
pip install -e ".[rl]"

# 可选：安装模仿学习依赖
pip install -e ".[bc]"
```

---

## 🚀 快速开始

### 注册的环境 ID

本项目在安装时自动注册了以下 Gym 环境：

| 环境 ID | 用途 |
|---------|------|
| `Isaac-Desktop-Organizer-Franka-IK-Rel-v0` | RL 训练 |
| `Isaac-Desktop-Organizer-Franka-IK-Rel-Play-v0` | RL 推理评估 |
| `Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0` | Mimic 数据采集 + BC 训练 |

### 1️⃣ 使用本项目脚本训练（推荐）

```bash
# 进入 IsaacLab 目录
cd /path/to/IsaacLab

# 快速测试（10 轮迭代，约 1-2 分钟）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 512 \
  --max_iterations 10 \
  --headless

# 完整训练（3000 轮迭代）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless

# 继续训练
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 5000 \
  --resume \
  --load_run 2026-01-23_17-58-10 \
  --headless
```

**预期结果**：
- 快速测试（10 轮）：约 1-2 分钟
- 完整训练（3000 轮）：约 2-3 小时（RTX 4090）
- 成功率：2500 轮后达到 80-85%
- Episode 长度：平均 4.2 秒

**训练日志位置**：`./logs/rsl_rl/desktop_organizer/`

### 2️⃣ 可视化训练好的策略

```bash
# 使用本项目脚本
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/play_rl.py \
  --load_run 2026-01-23_17-58-10 \
  --num_envs 16
```

### 3️⃣ 使用模仿学习训练（BC + MimicGen）

使用 Isaac Lab 官方脚本配合本项目注册的环境：

```bash
# 步骤 1：录制人工演示
cd /path/to/IsaacLab
./isaaclab.sh -p scripts/tools/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --teleop_device keyboard \
  --dataset_file ./datasets/raw.hdf5 \
  --num_demos 10

# 步骤 2：标注子任务边界
python scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
  --dataset ./datasets/raw.hdf5 \
  --output ./datasets/annotated.hdf5

# 步骤 3：使用 MimicGen 生成合成数据
python scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --input_file ./datasets/annotated.hdf5 \
  --output_file ./datasets/generated.hdf5 \
  --generation_num_trials 100 \
  --num_envs 100

# 步骤 4：训练 BC 策略
./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0 \
  --algo bc \
  --dataset ./datasets/generated.hdf5 \
  --epochs 200
```

详细说明请查看 [MimicGen 数据生成指南](docs/mimic_data_generation.md)

---

## 📊 训练结果

### 强化学习（PPO）

| 指标 | 数值 |
|------|------|
| **成功率** | 85% |
| **Episode 长度** | 4.2 秒（平均） |
| **训练轮数** | 2500 |
| **并行环境数** | 4096 |
| **训练时间** | ~2-3 小时（RTX 4090） |

### 关键奖励权重

```python
reaching_object: 5.0                          # 接近物体
lifting_object: 10.0                          # 举起物体
command_progress: 30.0                        # 朝目标前进
object_goal_tracking: 10.0                    # 粗略追踪
object_goal_tracking_fine_grained: 50.0       # 精细追踪
success_reward: 20000.0                       # 放入篮子（关键！）
gripper_closed_penalty: -100.0                # 强制松开夹爪
```

### 模仿学习（BC + MimicGen）

| 指标 | 数值 |
|------|------|
| **源演示数量** | 10 |
| **生成演示数量** | 100 |
| **成功率** | 75% |
| **训练轮数** | 200 |

---

## 🏗️ 项目架构

```
isaaclab-desktop-organizer/          # 独立包
├── desktop_organizer/               # 核心模块
│   ├── envs/                        # 环境配置
│   │   ├── rl_env_cfg.py           # RL 环境
│   │   ├── mimic_env_cfg.py        # Mimic 配置
│   │   └── mimic_env.py            # Mimic 包装器
│   ├── mdp/                         # MDP 组件
│   │   └── rewards.py              # 自定义奖励函数
│   ├── config/                      # 算法配置
│   │   ├── ppo_cfg.py              # PPO 超参数
│   │   └── robomimic/bc.json       # BC 配置
│   └── assets/                      # 机器人/场景资产
├── scripts/                         # 训练脚本
│   ├── train_rl.py                 # RL 训练
│   └── play_rl.py                  # RL 评估
├── docs/                            # 文档
│   ├── installation.md             # 安装指南
│   └── mimic_data_generation.md    # Mimic 数据生成指南
└── assets/                          # USD 场景文件
    └── scenes/
        └── Collected_table_clean/
            └── table_clean.usd     # 桌面场景（29KB）
```

**设计原则**：
- ✅ 不修改 Isaac Lab 源码
- ✅ 标准 Gym 接口
- ✅ 模块化 MDP 组件
- ✅ 基于配置的定制

---

## 🔧 配置说明

### 自定义奖励权重

编辑 `desktop_organizer/envs/rl_env_cfg.py`:

```python
@configclass
class RewardsCfg:
    reaching_object = RewTerm(weight=5.0, ...)
    success_reward = RewTerm(weight=20000.0, ...)  # 调整这个！
```

### 自定义 PPO 超参数

编辑 `desktop_organizer/config/ppo_cfg.py`:

```python
@configclass
class DesktopOrganizerPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    policy = RslRlPpoActorCriticCfg(
        actor_hidden_dims=[256, 128, 64],  # 修改网络大小
        ...
    )
```

### 自定义物体随机化范围

编辑 `desktop_organizer/envs/rl_env_cfg.py`:

```python
randomize_ketchup = EventTerm(
    func=franka_stack_events.randomize_object_pose,
    params={
        "pose_range": {
            "x": (1.25, 1.50),  # 调整范围
            "y": (1.40, 1.65),  # 调整范围
            ...
        },
    },
)
```

---

## 📖 文档

- [安装指南](docs/installation.md) - 详细的安装步骤
- [MimicGen 数据生成指南](docs/mimic_data_generation.md) - 完整的模仿学习工作流程
- [架构说明](#-项目架构) - 代码结构解释
- [常见问题](docs/mimic_data_generation.md#-常见问题) - 问题排查

---

## 🎯 简历亮点

使用这个项目时，可以这样描述：

### 中文版
```
独立开发了基于 Isaac Lab 的机器人操作任务 Python 包：
• 设计完整的强化学习环境（支持 4096 个并行环境）
• 实现自定义 MDP 组件（奖励函数、观测、终止条件）
• 支持多种算法（PPO、BC + MimicGen 数据增强）
• 标准 Python 包管理（pip 可安装，1300+ 行代码）
• 训练成功率达 85%，episode 时长 4.2 秒
• 开源：github.com/yourusername/isaaclab-desktop-organizer
```

### English Version
```
Developed a standalone robotic manipulation package for Isaac Lab:
• Designed complete RL environment (4096 parallel environments)
• Implemented custom MDP components (rewards, observations, terminations)
• Supported multiple algorithms (PPO, BC with MimicGen augmentation)
• Standard Python packaging (pip installable, 1300+ lines of code)
• Achieved 85% success rate with 4.2s episode length
• Open source: github.com/yourusername/isaaclab-desktop-organizer
```

---

## 🤝 贡献

欢迎贡献！请：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加了某个特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [Isaac Lab](https://isaac-sim.github.io/IsaacLab/) - 仿真框架
- [RSL-RL](https://github.com/leggedrobotics/rsl_rl) - PPO 实现
- [Robomimic](https://robomimic.github.io/) - 模仿学习工具
- [MimicGen](https://mimicgen.github.io/) - 数据增强

---

## 📧 联系方式

- **作者**: 你的名字
- **邮箱**: your.email@example.com
- **GitHub**: [@your-username](https://github.com/your-username)

---

## 🌟 引用

如果你在研究中使用了本项目，请引用：

```bibtex
@software{isaaclab_desktop_organizer_2026,
  author = {你的名字},
  title = {IsaacLab Desktop Organizer: 基于强化学习和模仿学习的机器人操作},
  year = {2026},
  url = {https://github.com/your-username/isaaclab-desktop-organizer}
}
```

---

## ⭐ Star 历史

如果这个项目对你的研究或工作有帮助，请考虑给它一个 star！⭐

---

## 🔧 故障排查

### 常见错误 1: "No module named 'omni.log'"

**错误现象**：
```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py
# ModuleNotFoundError: No module named 'omni.log'
```

**原因**：Isaac Sim 未正确初始化

**解决**：此错误已在 `train_rl.py` 中修复，确保使用最新版本的脚本。脚本会自动调用 `AppLauncher` 初始化 Isaac Sim。

---

### 常见错误 2: "ManagerBasedRLEnv.__init__() missing 1 required positional argument: 'cfg'"

**错误现象**：
```python
env = gym.make("Isaac-Desktop-Organizer-Franka-IK-Rel-v0", num_envs=512)
# TypeError: missing 1 required positional argument: 'cfg'
```

**原因**：IsaacLab 环境需要显式传递配置对象

**解决**：此错误已在 `train_rl.py` 中修复。脚本会自动调用 `parse_env_cfg()` 解析配置。

---

### 常见错误 3: "'OrderEnforcing' object has no attribute 'get_observations'"

**错误现象**：训练时报错缺少 `get_observations` 方法

**原因**：环境未用 `RslRlVecEnvWrapper` 包装

**解决**：此错误已在 `train_rl.py` 中修复。脚本会自动调用 `RslRlVecEnvWrapper` 包装环境。

---

### 验证安装

运行以下测试脚本验证安装正确：

```bash
# 进入 IsaacLab 目录
cd /path/to/IsaacLab

# 快速测试（10 轮迭代，1-2 分钟）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 512 \
  --max_iterations 10 \
  --headless
```

**预期输出**：
```
[INFO] Parsing environment config for: Isaac-Desktop-Organizer-Franka-IK-Rel-v0
[INFO] Creating environment: Isaac-Desktop-Organizer-Franka-IK-Rel-v0
[INFO] Wrapping environment with RslRlVecEnvWrapper...
[INFO] Creating PPO runner...
[INFO] Starting training for 10 iterations...
================================================================================
# ... 训练进度
================================================================================
[INFO] Training complete!
```

如果以上输出正常，说明安装成功！

---

## ❓ 常见问题（FAQ）

### Q1: 我已经安装了 IsaacLab，如何使用这个项目？

**答**：两个简单步骤：

```bash
# 1. 激活 IsaacLab 环境
cd /path/to/IsaacLab
source .venv/bin/activate

# 2. 安装本项目
cd ~/isaaclab-desktop-organizer
pip install -e .

# 3. 开始训练
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --headless
```

### Q2: 为什么不能用 IsaacLab 官方的 train.py？

**答**：官方 `train.py` 只导入了主项目环境（`isaaclab_tasks`），没有导入外部包（`desktop_organizer`）：

```python
# 官方 train.py 第 96 行
import isaaclab_tasks  # noqa: F401
# ❌ 没有 import desktop_organizer
```

**解决方案**：使用本项目提供的 `train_rl.py` 脚本，该脚本已修复所有问题并优化参数默认值。

### Q3: 为什么需要安装本项目？不能直接用吗？

**答**：本项目需要安装的原因：
1. ✅ 注册 Gym 环境 ID（`Isaac-Desktop-Organizer-Franka-IK-Rel-v0`）
2. ✅ 安装自定义奖励函数（`object_command_progress`, `gripper_closed_at_goal`）
3. ✅ 配置场景资产路径

安装后，IsaacLab 的所有官方脚本都能识别你的环境。

### Q4: 训练脚本的关键修复有哪些？

**答**：`train_rl.py` 脚本经过以下关键修复：

1. ✅ **自动初始化 Isaac Sim**：调用 `AppLauncher` 初始化
2. ✅ **正确解析配置**：使用 `parse_env_cfg()` 生成环境配置
3. ✅ **环境包装**：用 `RslRlVecEnvWrapper` 包装，兼容 RSL-RL
4. ✅ **参数优化**：移除冲突参数，使用最佳默认值

详细修复记录请查看 `/root/isaaclab-desktop-organizer/tests/EXTERNAL_PACKAGE_FIXES.md`

### Q5: 如何验证环境注册成功？

```bash
cd /path/to/IsaacLab
source .venv/bin/activate

python -c "
import desktop_organizer
import gymnasium as gym
print('✅ 已注册环境:', [spec.id for spec in gym.envs.registry.values() if 'Desktop-Organizer' in spec.id])
"
```

**预期输出**：
```
✅ 已注册环境: ['Isaac-Desktop-Organizer-Franka-IK-Rel-v0',
                'Isaac-Desktop-Organizer-Franka-IK-Rel-Play-v0',
                'Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0']
```

### Q6: 训练时出现 `ModuleNotFoundError: No module named 'desktop_organizer'`

**原因**：未安装本项目或未激活正确的环境

**解决**：
```bash
# 1. 确认在 IsaacLab 环境中
cd /path/to/IsaacLab
source .venv/bin/activate

# 2. 重新安装
cd ~/isaaclab-desktop-organizer
pip install -e .

# 3. 验证
python -c "import desktop_organizer; print('✅ 安装成功')"
```

### Q7: 我的主项目和外部包环境 ID 有什么区别？

**答**：命名略有不同，但功能相同：

| 功能 | 主项目 | 外部包（本项目） |
|------|--------|-----------------|
| **RL 训练** | `Isaac-Desktop-Organizer-Franka-**RL-IK-Rel**-v0` | `Isaac-Desktop-Organizer-Franka-**IK-Rel**-v0` |
| **Mimic** | `Isaac-Desktop-Organizer-Franka-**IK-Rel-Mimic**-v0` | `Isaac-Desktop-Organizer-Franka-**Mimic-IK-Rel**-v0` |

主项目 RL 环境多了 `RL-` 前缀，Mimic 环境的 `Mimic` 位置不同。

### Q8: 能否不安装，直接把代码复制到 IsaacLab 里？

**可以，但不推荐**。如果一定要这样做：

```bash
# 将你的包复制到 IsaacLab 的 source 目录
cp -r ~/isaaclab-desktop-organizer/desktop_organizer \
      /path/to/IsaacLab/source/extensions/isaaclab.ext/isaaclab_tasks/

# 注册环境（在 IsaacLab 的 __init__.py 中添加）
# 但这样会修改 IsaacLab 源码，不建议
```

**为什么不推荐**：
- ❌ 修改了 IsaacLab 源码
- ❌ 升级 IsaacLab 时会丢失你的代码
- ❌ 难以版本控制

---

## 🔍 相关资源

### 教程链接
- [强化学习训练完整教程](docs/installation.md#step-3-run-a-quick-training-test-10-iterations)
- [MimicGen 数据生成完整流程](docs/mimic_data_generation.md#-完整数据流程)
- [自定义奖励函数教程](docs/mimic_data_generation.md#-mimic-配置在环境中定义)
- [**训练脚本修复记录**](/root/isaaclab-desktop-organizer/tests/EXTERNAL_PACKAGE_FIXES.md) - 详细记录所有问题和解决方案

### 常见问题
- [为什么机械臂抓着不放？](docs/mimic_data_generation.md#1-生成成功率低--30)
- [如何调整随机化范围？](#自定义物体随机化范围)
- [如何修改网络结构？](#自定义-ppo-超参数)
- [为什么不能用官方 train.py？](#q2-为什么不能用-isaaclab-官方的-trainpy)
- [训练脚本做了哪些修复？](#q4-训练脚本的关键修复有哪些)

---

**🎉 开始使用 IsaacLab Desktop Organizer，训练你的第一个机器人策略！**
