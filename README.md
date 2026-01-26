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

1. **Isaac Lab 0.5.0+** - 按照[官方安装指南](https://isaac-sim.github.io/IsaacLab/source/setup/installation.html)安装
2. **Python 3.10+**
3. **CUDA 11.8+**（用于 GPU 加速）

### 安装本包

```bash
# 方案 1：从源码安装（推荐，用于开发）
git clone https://github.com/<your-username>/isaaclab-desktop-organizer.git
cd isaaclab-desktop-organizer
pip install -e .

# 方案 2：从 PyPI 安装（发布后可用）
pip install isaaclab-desktop-organizer

# 可选：安装强化学习依赖
pip install -e ".[rl]"

# 可选：安装模仿学习依赖
pip install -e ".[bc]"
```

---

## 🚀 快速开始

### 1️⃣ 使用强化学习训练（PPO）

```bash
# 从头训练
python scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless

# 继续训练
python scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 5000 \
  --resume \
  --load_run 2026-01-23_17-58-10
```

**预期结果**：
- 训练时间：~2-3 小时（RTX 4090）
- 成功率：2500 轮后达到 80-85%
- Episode 长度：平均 4.2 秒

### 2️⃣ 可视化训练好的策略

```bash
python scripts/play_rl.py \
  --load_run 2026-01-23_17-58-10 \
  --num_envs 16
```

### 3️⃣ 使用模仿学习训练（BC + MimicGen）

使用 Isaac Lab 官方脚本配合你注册的环境：

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

## 🔍 相关资源

### 教程链接
- [强化学习训练完整教程](docs/installation.md#step-3-run-a-quick-training-test-10-iterations)
- [MimicGen 数据生成完整流程](docs/mimic_data_generation.md#-完整数据流程)
- [自定义奖励函数教程](docs/mimic_data_generation.md#-mimic-配置在环境中定义)

### 常见问题
- [为什么机械臂抓着不放？](docs/mimic_data_generation.md#1-生成成功率低--30)
- [如何调整随机化范围？](#自定义物体随机化范围)
- [如何修改网络结构？](#自定义-ppo-超参数)

---

**🎉 开始使用 IsaacLab Desktop Organizer，训练你的第一个机器人策略！**
