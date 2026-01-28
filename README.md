# 🤖 IsaacLab 桌面收纳任务

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Isaac Lab](https://img.shields.io/badge/Isaac%20Lab-0.53.0+-green.svg)](https://isaac-sim.github.io/IsaacLab/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个**专业级的强化学习独立包**，用于 Isaac Lab 中的 Franka 机械臂操作任务。训练机器人将物体抓取并放入篮子，支持最先进的强化学习和模仿学习算法。

---

## ✨ 特性

| 功能 | 说明 |
|------|------|
| **任务** | 抓取 ketchup 并放入篮子（可扩展到 3+ 个物体） |
| **机器人** | Franka Panda 机械臂 + 平行夹爪 |
| **控制方式** |  IK（相对位姿控制） |
| **观测空间** | 关节状态 + 物体位姿  |
| **奖励设计** | 稠密奖励：接近、抓取、举起、追踪 |
| **数据增强** | MimicGen（10 条演示 → 100+ 条） |
| **算法支持** | RSL-RL (PPO) + Robomimic (BC) |
| **并行训练** | 4096 个并行环境，快速训练 |



---

## 📦 安装

### 前置要求

1. **Isaac Lab 0.53.0+** 

```bash
# 克隆 Isaac Lab 仓库
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# 按照官方指南安装
# 详见: https://isaac-sim.github.io/IsaacLab/source/setup/installation.html
./isaaclab.sh --install
```

2. **Python 3.11+**
3. **CUDA 12.8+**

### 安装本包


```bash
# 激活 IsaacLab 环境
cd /path/to/IsaacLab
source .venv/bin/activate  # Linux/Mac
# 或者 .venv\Scripts\activate  # Windows

# 克隆本仓库
cd ..
git clone https://github.com/sawfnalfhg/isaaclab-desktop-organizer.git
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
| `Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0` | Mimic 数据采集 + BC 训练 |

### 1️⃣ 使用本项目脚本训练

```bash
# 进入 IsaacLab 目录
cd /path/to/IsaacLab

# 快速测试
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/rl/train_rl.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0 \
  --num_envs 512 \
  --max_iterations 10 \
  --headless

# 完整训练
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/rl/train_rl.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0 \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless

# 继续训练（查找最新的训练运行）
LATEST_RUN=$(ls -t ./logs/rsl_rl/desktop_organizer/ | head -1)
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/rl/train_rl.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0 \
  --num_envs 4096 \
  --max_iterations 5000 \
  --resume \
  --load_run $LATEST_RUN \
  --headless
```

**说明**：
- `--load_run` 参数是一个**时间戳格式的文件夹名**（如 `2026-01-23_17-58-10`）
- 每次训练都会创建**新的时间戳文件夹**，不会覆盖之前的模型
- Resume 训练会从指定的检查点加载，但保存到新的文件夹
- 使用 `ls -t ./logs/rsl_rl/desktop_organizer/ | head -1` 可以找到最新的训练运行

**预期结果**：
- 快速测试（10 轮）：约 1-2 分钟
- 完整训练（3000 轮）：约 2-3 小时（RTX 4090）
- 成功率：2500 轮后达到 95%


**训练日志位置**：`./logs/rsl_rl/desktop_organizer/{timestamp}/`

**查看所有训练运行**：
```bash
ls -lt ./logs/rsl_rl/desktop_organizer/
```

### 2️⃣ 可视化训练好的策略

```bash
# 找到最新的训练运行
LATEST_RUN=$(ls -t ./logs/rsl_rl/desktop_organizer/ | head -1)

# 使用本项目脚本评估
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/rl/play_rl.py \
  --load_run $LATEST_RUN \
  --num_envs 16
```



### 3️⃣ 使用模仿学习训练（BC + MimicGen）

**重要**：外部包必须使用专用脚本（位于 `/root/isaaclab-desktop-organizer/scripts/`），不能使用 IsaacLab 官方脚本（官方脚本不导入外部包）。

```bash
cd /path/to/IsaacLab

# 步骤 1：录制人工演示（10 条）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/bc/record_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --teleop_device keyboard \
  --dataset_file ./datasets/raw.hdf5 \
  --num_demos 10

# 步骤 2：标注子任务边界
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/bc/annotate_demos.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --input_file ./datasets/raw.hdf5 \
  --output_file ./datasets/annotated.hdf5

# 步骤 3：使用 MimicGen 生成合成数据（100 条）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/bc/generate_dataset.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --input_file ./datasets/annotated.hdf5 \
  --output_file ./datasets/generated.hdf5 \
  --generation_num_trials 100 \
  --num_envs 100 \
  --headless

# 步骤 4：训练 BC 策略（200 轮）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/bc/train_bc.py \
  --task Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0 \
  --algo bc \
  --dataset ./datasets/generated.hdf5 \
  --epochs 200

  ### Step 5: 评估训练好的 BC 策略

```bash
# 步骤 5: 使用训练好的 BC 模型进行评估
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/bc/play_bc.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-Mimic-v0 \
  --checkpoint ./logs/robomimic/Isaac-Desktop-Organizer-Franka-IK-Rel-Mimic-v0/bc/<timestamp>/models/model_epoch_200.pth \
  --num_envs 1 \
  --num_rollouts 10
```

**为什么必须用外部包脚本？**

IsaacLab 官方脚本只导入主项目环境（`isaaclab_tasks`），不导入外部包（`desktop_organizer`）。详见 [外部包工具脚本完整指南](/root/isaaclab-desktop-organizer/tests/EXTERNAL_PACKAGE_SCRIPTS_GUIDE.md)。

详细说明请查看 [MimicGen 数据生成指南](docs/mimic_data_generation.md)

---

## 📊 训练结果

### 强化学习（PPO）

| 指标 | 数值 |
|------|------|
| **成功率** | 95% |
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
| **成功率** | 50% |
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
│   ├── rl/                          # 强化学习脚本
│   │   ├── train_rl.py             # RL 训练
│   │   └── play_rl.py              # RL 评估
│   └── bc/                          # 模仿学习脚本
│       ├── record_demos.py         # 录制演示
│       ├── annotate_demos.py       # 标注子任务
│       ├── generate_dataset.py     # 生成数据
│       ├── train_bc.py             # BC 训练
│       └── play_bc.py              # BC 评估
├── docs/                            # 文档
│   ├── installation.md             # 安装指南
│   └── mimic_data_generation.md    # Mimic 数据生成指南
└── assets/                          # USD 场景文件
    └── scenes/
        └── Collected_table_clean/
            └── table_clean.usd     # 桌面场景（29KB）
```

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

## 📖 文档

### 使用指南
- [安装指南](docs/installation.md) - 详细的安装步骤
- [MimicGen 数据生成指南](docs/mimic_data_generation.md) - 完整的模仿学习工作流程
- [架构说明](#-项目架构) - 代码结构解释
- [常见问题](docs/mimic_data_generation.md#-常见问题) - 问题排查

### 技术文档
- **[Bug 修复总结 (2026-01-27)](../../root/isaaclab-desktop-organizer/tests/BUG_FIX_SUMMARY_2026-01-27.md)** - 脚本完全对齐官方版本的详细说明
- **[脚本对齐完成报告](../../root/isaaclab-desktop-organizer/tests/SCRIPTS_ALIGNMENT_COMPLETE.md)** - 功能对比和验证方法
- [外部包工具脚本完整指南](../../root/isaaclab-desktop-organizer/tests/EXTERNAL_PACKAGE_SCRIPTS_GUIDE.md) - 为什么需要外部包专用脚本

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

- **作者**: zql
- **邮箱**: zhangqianli58@gmail.com
- **GitHub**: [sawfnalfhg](https://github.com/sawfnalfhg)

---

## 🌟 引用

如果你在研究中使用了本项目，请引用：

```bibtex
@software{isaaclab_desktop_organizer_2026,
  author = {sawfnalfhg},
  title = {IsaacLab Desktop Organizer: 基于强化学习和模仿学习的桌面收纳任务},
  year = {2026},
  url = {https://github.com/sawfnalfhg/isaaclab-desktop-organizer}
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

### 技术文档（重要！）
- **[Bug 修复总结 (2026-01-27)](../../root/isaaclab-desktop-organizer/tests/BUG_FIX_SUMMARY_2026-01-27.md)** ⭐ 脚本完全对齐官方版本的详细说明
- **[脚本对齐完成报告](../../root/isaaclab-desktop-organizer/tests/SCRIPTS_ALIGNMENT_COMPLETE.md)** - 功能对比和验证方法
- [外部包工具脚本完整指南](../../root/isaaclab-desktop-organizer/tests/EXTERNAL_PACKAGE_SCRIPTS_GUIDE.md) - 为什么需要外部包专用脚本

### 常见问题
- [为什么机械臂抓着不放？](docs/mimic_data_generation.md#1-生成成功率低--30)
- [如何调整随机化范围？](#自定义物体随机化范围)
- [如何修改网络结构？](#自定义-ppo-超参数)
- [为什么不能用官方 train.py？](#q2-为什么不能用-isaaclab-官方的-trainpy)
- [训练脚本与官方有什么区别？](#q4-训练脚本与官方有什么区别)

---

**🎉 开始使用 IsaacLab Desktop Organizer，训练你的第一个机器人策略！**
