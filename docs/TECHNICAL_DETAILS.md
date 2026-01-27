# 技术细节文档

本文档包含 Desktop Organizer 项目的详细技术信息、配置说明和常见问题解答。

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

### 设计原则

- ✅ **不修改 Isaac Lab 源码** - 作为外部包独立维护
- ✅ **标准 Gym 接口** - 遵循 Gymnasium 标准
- ✅ **模块化 MDP 组件** - 观测、奖励、终止条件分离
- ✅ **基于配置的定制** - 通过配置文件而非硬编码调整参数

---

## 🔧 配置说明

### 自定义奖励权重

编辑 `desktop_organizer/envs/rl_env_cfg.py`:

```python
@configclass
class RewardsCfg:
    # 接近物体奖励
    reaching_object = RewTerm(weight=5.0, ...)

    # 举起物体奖励
    lifting_object = RewTerm(weight=10.0, ...)

    # 整体进度奖励
    command_progress = RewTerm(weight=30.0, ...)

    # 目标追踪奖励
    object_goal_tracking = RewTerm(weight=10.0, ...)
    object_goal_tracking_fine_grained = RewTerm(weight=50.0, ...)

    # 成功奖励（关键！）
    success_reward = RewTerm(weight=20000.0, ...)  # 必须远大于持续奖励总和

    # 惩罚项
    gripper_closed_penalty = RewTerm(weight=-100.0, ...)  # 强制松开夹爪
```

**调优建议**：
- `success_reward` 应该 > 所有持续奖励的累积和
- `gripper_closed_penalty` 防止机械臂抓着不放
- 泛化时增加 `reaching_object` 权重

### 自定义 PPO 超参数

编辑 `desktop_organizer/config/ppo_cfg.py`:

```python
@configclass
class DesktopOrganizerPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    # 训练步数
    num_steps_per_env = 24
    max_iterations = 3000

    # 网络结构
    policy = RslRlPpoActorCriticCfg(
        actor_hidden_dims=[256, 128, 64],  # 修改 Actor 网络大小
        critic_hidden_dims=[256, 128, 64], # 修改 Critic 网络大小
        activation="elu",
    )

    # 学习率
    learning_rate = 1e-3

    # PPO 参数
    clip_param = 0.2
    entropy_coef = 0.01
```

**调优建议**：
- 增大网络容量可以提高性能，但训练会更慢
- 降低学习率可以提高稳定性
- 调整 `clip_param` 和 `entropy_coef` 平衡探索和利用

### 自定义物体随机化范围

编辑 `desktop_organizer/envs/rl_env_cfg.py`:

```python
randomize_objects_positions = EventTerm(
    func=randomize_objects_xy_keep_z,
    mode="reset",
    params={
        "per_object_pose_ranges": [
            # Orange juice - 大范围随机（干扰物）
            {
                "x": (1.10, 1.50),  # 40cm 范围
                "y": (1.30, 1.75),  # 45cm 范围
                "roll": (1.5708, 1.5708),
                "pitch": (0.0, 0.0),
                "yaw": (-0.5, 0.5),
            },
            # Ketchup - 小范围随机（目标物体）
            {
                "x": (1.25, 1.50),  # 25cm 范围（泛化版）
                "y": (1.40, 1.65),  # 25cm 范围（泛化版）
                "roll": (1.5708, 1.5708),
                "pitch": (0.0, 0.0),
                "yaw": (-0.15, 0.15),
            },
            # Cream cheese - 大范围随机（干扰物）
            {
                "x": (1.10, 1.50),
                "y": (1.30, 1.75),
                "roll": (1.5708, 1.5708),
                "pitch": (0.0, 0.0),
                "yaw": (-0.5, 0.5),
            },
        ],
        "min_separation": 0.10,  # 物体最小间距 10cm
        "asset_cfgs": [
            SceneEntityCfg("orange_juice"),
            SceneEntityCfg("ketchup"),
            SceneEntityCfg("cream_cheese"),
        ],
        "z_values": [0.52, 0.50771, 0.45974],  # 固定高度
    },
)
```

**调优建议**：
- 目标物体范围越小，训练越快，但泛化性越差
- `min_separation` 太大会导致采样失败
- 逐步扩大随机范围（curriculum learning）

---

## ❓ 常见问题（FAQ）

### Q1: 我已经安装了 IsaacLab，如何使用这个项目？

**答**：三个简单步骤：

```bash
# 1. 激活 IsaacLab 环境
cd /path/to/IsaacLab
source .venv/bin/activate

# 2. 安装本项目
cd ~/isaaclab-desktop-organizer
pip install -e .

# 3. 开始训练
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0 \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless
```

---

### Q2: 为什么不能用 IsaacLab 官方的 train.py？

**答**：官方 `train.py` 只导入了主项目环境（`isaaclab_tasks`），没有导入外部包（`desktop_organizer`）：

```python
# 官方 train.py 第 96 行
import isaaclab_tasks  # noqa: F401
# ❌ 没有 import desktop_organizer
```

**解决方案**：使用本项目提供的 `train_rl.py` 脚本。该脚本是**官方 train.py 的完整副本**，唯一的修改是添加了一行：

```python
import isaaclab_tasks  # noqa: F401
import desktop_organizer  # noqa: F401  # ← 唯一添加的行
```

这样外部包环境就能被识别，同时保持与官方脚本**完全相同**的功能（Hydra 配置、种子设置、配置导出、Git 追踪、视频录制、多 GPU 支持等）。

---

### Q3: 为什么需要安装本项目？不能直接用吗？

**答**：本项目需要安装的原因：

1. ✅ **注册 Gym 环境 ID**（`Isaac-Desktop-Organizer-Franka-IK-Rel-v0`）
2. ✅ **安装自定义奖励函数**（`object_command_progress`, `gripper_closed_at_goal`）
3. ✅ **配置场景资产路径**

安装后，IsaacLab 的工具脚本就能识别你的环境。

---

### Q4: 训练脚本与官方有什么区别？

**答**：本项目的所有脚本（`train_rl.py`, `play_rl.py`, `record_demos.py` 等）都是**官方脚本的完整副本**，功能完全一致，包括：

1. ✅ **Hydra 配置系统**：动态加载环境和算法配置
2. ✅ **种子设置**：`env_cfg.seed = agent_cfg.seed` 确保可重现性
3. ✅ **配置文件导出**：自动保存 yaml 和 pickle 配置文件
4. ✅ **Git 仓库追踪**：`runner.add_git_repo_to_log()` 记录代码版本
5. ✅ **视频录制**：`--video` 参数支持训练可视化
6. ✅ **多 GPU 训练**：`--distributed` 参数支持分布式训练
7. ✅ **动态时间戳文件夹**：每次训练创建新的 `YYYY-MM-DD_HH-MM-SS` 文件夹

**唯一修改**：添加了一行 `import desktop_organizer  # noqa: F401`，使外部包环境能被识别。

详细说明请查看 [/root/isaaclab-desktop-organizer/tests/SCRIPTS_ALIGNMENT_COMPLETE.md](../../root/isaaclab-desktop-organizer/tests/SCRIPTS_ALIGNMENT_COMPLETE.md)

---

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
                'Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0']
```

---

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

---

### Q7: 我的主项目和外部包环境 ID 有什么区别？

**答**：命名略有不同，但功能相同：

| 功能 | 主项目 | 外部包（本项目） |
|------|--------|-----------------|
| **RL 训练** | `Isaac-Desktop-Organizer-Franka-**RL-IK-Rel**-v0` | `Isaac-Desktop-Organizer-Franka-**IK-Rel**-v0` |
| **Mimic** | `Isaac-Desktop-Organizer-Franka-**IK-Rel-Mimic**-v0` | `Isaac-Desktop-Organizer-Franka-**Mimic-IK-Rel**-v0` |

主项目 RL 环境多了 `RL-` 前缀，Mimic 环境的 `Mimic` 位置不同。

---

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

## 🎯 简历亮点

如果你使用本项目进行研究或学习，可以这样描述：

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
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0 \
  --num_envs 512 \
  --max_iterations 10 \
  --headless
```

**预期输出**：
```
[INFO] Logging experiment in directory: ...
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

## 📚 相关文档

- [Bug 修复总结 (2026-01-27)](../../root/isaaclab-desktop-organizer/tests/BUG_FIX_SUMMARY_2026-01-27.md) - 脚本完全对齐官方版本的详细说明
- [脚本对齐完成报告](../../root/isaaclab-desktop-organizer/tests/SCRIPTS_ALIGNMENT_COMPLETE.md) - 功能对比和验证方法
- [外部包工具脚本完整指南](../../root/isaaclab-desktop-organizer/tests/EXTERNAL_PACKAGE_SCRIPTS_GUIDE.md) - 为什么需要外部包专用脚本
- [MimicGen 数据生成指南](../mimic_data_generation.md) - 完整的模仿学习工作流程
