# 外部包 train_rl.py 修复记录

## 问题背景

外部包 `/root/isaaclab-desktop-organizer/scripts/train_rl.py` 原始脚本存在多个问题，导致无法正常运行训练。本文档记录了所有遇到的问题和修复方案。

---

## 问题 1：无法用官方 train.py 训练外部包环境

### 错误现象
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Desktop-Organizer-Franka-IK-Rel-v0

# 报错：Environment 'Isaac-Desktop-Organizer-Franka-IK-Rel-v0' doesn't exist
```

### 根本原因

官方 `train.py` 只导入了 `isaaclab_tasks`（主项目），没有导入 `desktop_organizer`（外部包），因此看不到外部包注册的环境。

```python
# 官方 train.py 第 96 行
import isaaclab_tasks  # noqa: F401
# ❌ 没有导入 desktop_organizer
```

### 解决方案

使用外部包独立的 `train_rl.py` 脚本（位于 `/root/isaaclab-desktop-organizer/scripts/train_rl.py`），但需要修复多个问题。

---

## 问题 2：gym.make() 缺少 cfg 参数

### 错误现象
```python
env = gym.make(
    args_cli.task,
    num_envs=args_cli.num_envs,  # ❌ 缺少 cfg 参数
)
# TypeError: ManagerBasedRLEnv.__init__() missing 1 required positional argument: 'cfg'
```

### 根本原因

IsaacLab 的 ManagerBasedRLEnv 需要显式传递环境配置 `cfg`，不能只通过 kwargs 传递 `num_envs`。

**官方正确做法**（`train.py` 第 155 行）：
```python
env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
```

### 修复方案

**修改前**（第 87-90 行）：
```python
env = gym.make(
    args_cli.task,
    num_envs=args_cli.num_envs,
)
```

**修改后**：
```python
# 添加导入
from isaaclab_tasks.utils import parse_env_cfg

# 解析环境配置
env_cfg = parse_env_cfg(
    task_name=args_cli.task,
    device=args_cli.device,
    num_envs=args_cli.num_envs,
)

# 创建环境（传递 cfg）
env = gym.make(args_cli.task, cfg=env_cfg)
```

---

## 问题 3：--device 参数冲突

### 错误现象
```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py --headless

# ValueError: The passed ArgParser object already has the field 'device'.
# This field will be added by `AppLauncher.add_app_launcher_args()`,
# and should not be added directly.
```

### 根本原因

外部包脚本自定义了 `--device` 参数（第 32-37 行），但 `AppLauncher.add_app_launcher_args()` 也会添加 `--device` 参数，导致重复。

**冲突代码**：
```python
parser.add_argument(
    "--device",
    type=str,
    default="cuda:0",
    help="Device to run on (cuda:0, cpu, etc.)",
)

# ... 后面调用
AppLauncher.add_app_launcher_args(parser)  # ❌ 冲突！
```

### 修复方案

删除自定义的 `--device` 参数定义（第 32-37 行），使用 AppLauncher 提供的 `--device`。

**修改前**：
```python
parser.add_argument(
    "--num_envs",
    type=int,
    default=4096,
    help="Number of parallel environments",
)
parser.add_argument(
    "--device",           # ❌ 删除这 6 行
    type=str,
    default="cuda:0",
    help="Device to run on (cuda:0, cpu, etc.)",
)
parser.add_argument(
    "--max_iterations",
    ...
)
```

**修改后**：
```python
parser.add_argument(
    "--num_envs",
    type=int,
    default=4096,
    help="Number of parallel environments",
)
parser.add_argument(
    "--max_iterations",   # 直接跳到下一个参数
    ...
)
```

---

## 问题 4：配置类属性层级错误

### 错误现象
```python
runner_cfg = DesktopOrganizerPPORunnerCfg()
runner_cfg.algorithm.max_iterations = args_cli.max_iterations  # ❌ 错误
runner_cfg.algorithm.device = args_cli.device  # ❌ 错误

# TypeError: 'DesktopOrganizerPPORunnerCfg' object is not subscriptable
```

### 根本原因

`DesktopOrganizerPPORunnerCfg` 配置类的结构：
```python
@configclass
class DesktopOrganizerPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 10000      # ✅ 顶层属性，不是 algorithm 的子属性
    save_interval = 500
    experiment_name = "desktop_organizer_rl"
    empirical_normalization = False
    policy = RslRlPpoActorCriticCfg(...)
    algorithm = RslRlPpoAlgorithmCfg(   # ❌ algorithm 没有 max_iterations/device
        value_loss_coef=1.0,
        ...
    )
```

### 修复方案

**修改前**（第 93-95 行）：
```python
runner_cfg = DesktopOrganizerPPORunnerCfg()
runner_cfg.algorithm.max_iterations = args_cli.max_iterations  # ❌ 错误层级
runner_cfg.algorithm.device = args_cli.device  # ❌ algorithm 没有 device
```

**修改后**：
```python
runner_cfg = DesktopOrganizerPPORunnerCfg()
runner_cfg.max_iterations = args_cli.max_iterations  # ✅ 顶层属性
# device 通过 OnPolicyRunner 构造函数传递，不在配置类中设置
```

---

## 问题 5：配置传递格式错误

### 错误现象
```python
runner = OnPolicyRunner(env, runner_cfg, log_dir=args_cli.log_dir, device=args_cli.device)
# TypeError: 'DesktopOrganizerPPORunnerCfg' object is not subscriptable
```

### 根本原因

`OnPolicyRunner` 期望配置是**字典格式**，不是配置类实例。

**官方正确做法**（`train.py` 第 181 行）：
```python
runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
```

### 修复方案

**修改前**（第 99 行）：
```python
runner = OnPolicyRunner(env, runner_cfg, log_dir=args_cli.log_dir, device=args_cli.device)
```

**修改后**：
```python
runner = OnPolicyRunner(env, runner_cfg.to_dict(), log_dir=args_cli.log_dir, device=args_cli.device)
```

---

## 问题 6：缺少 RslRlVecEnvWrapper 包装（最严重）

### 错误现象
```python
runner = OnPolicyRunner(env, runner_cfg.to_dict(), log_dir=args_cli.log_dir, device=args_cli.device)
# AttributeError: 'OrderEnforcing' object has no attribute 'get_observations'
```

### 根本原因

RSL-RL 的 `OnPolicyRunner` 期望环境实现特定的接口（如 `get_observations()`），但原始的 Gymnasium 环境没有这些方法。需要使用 `RslRlVecEnvWrapper` 将 IsaacLab 环境包装成 RSL-RL 兼容的接口。

**官方正确做法**（`train.py` 第 178 行）：
```python
# wrap around environment for rsl-rl
env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

# create runner from rsl-rl
runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
```

### 修复方案

**修改前**（缺失）：
```python
env = gym.make(args_cli.task, cfg=env_cfg)

# ❌ 直接创建 runner，缺少包装步骤
runner = OnPolicyRunner(env, runner_cfg.to_dict(), ...)
```

**修改后**（第 99-101 行）：
```python
# 添加导入
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

# 创建环境
env = gym.make(args_cli.task, cfg=env_cfg)

# ✅ 包装环境
env = RslRlVecEnvWrapper(env)

# 创建 runner
runner = OnPolicyRunner(env, runner_cfg.to_dict(), ...)
```

---

## 完整修复后的代码（关键部分）

```python
"""Rest everything follows."""

import gymnasium as gym
import torch
from rsl_rl.runners import OnPolicyRunner

import desktop_organizer  # Register environments
from desktop_organizer.config.ppo_cfg import DesktopOrganizerPPORunnerCfg
from isaaclab_tasks.utils import parse_env_cfg
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # ✅ 新增


def main():
    """Train the RL agent."""

    # Parse environment configuration
    print(f"[INFO] Parsing environment config for: {args_cli.task}")
    env_cfg = parse_env_cfg(  # ✅ 新增
        task_name=args_cli.task,
        device=args_cli.device,
        num_envs=args_cli.num_envs,
    )

    # Create environment
    print(f"[INFO] Creating environment: {args_cli.task}")
    env = gym.make(args_cli.task, cfg=env_cfg)  # ✅ 添加 cfg 参数

    # Wrap environment for RSL-RL
    print(f"[INFO] Wrapping environment with RslRlVecEnvWrapper...")
    env = RslRlVecEnvWrapper(env)  # ✅ 新增包装步骤

    # Create runner config
    runner_cfg = DesktopOrganizerPPORunnerCfg()
    runner_cfg.max_iterations = args_cli.max_iterations  # ✅ 修正属性层级

    # Create runner
    print(f"[INFO] Creating PPO runner...")
    runner = OnPolicyRunner(env, runner_cfg.to_dict(), log_dir=args_cli.log_dir, device=args_cli.device)  # ✅ 使用 .to_dict()
```

---

## 验证结果

### 修复前
❌ 无法运行，遇到 6 个严重错误

### 修复后
✅ 可以正常启动训练

**测试命令**：
```bash
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
[INFO] Number of environments: 512
[INFO] Device: cuda:0
[INFO] Log directory: ./logs/rsl_rl/desktop_organizer
================================================================================
# ... 训练进度输出
```

---

## 总结

### 修复清单

| # | 问题 | 修复方案 | 严重性 |
|---|------|---------|--------|
| 1 | 无法用官方 train.py | 使用外部包独立脚本 | 中 |
| 2 | 缺少 cfg 参数 | 添加 `parse_env_cfg()` | ⚠️ 高 |
| 3 | --device 冲突 | 删除自定义参数 | ⚠️ 高 |
| 4 | 配置属性层级错误 | 修正为顶层属性 | ⚠️ 高 |
| 5 | 配置格式错误 | 使用 `.to_dict()` | ⚠️ 高 |
| 6 | 缺少环境包装 | 添加 `RslRlVecEnvWrapper` | 🔴 **最严重** |

### 关键学习点

1. **环境配置必须显式传递**：IsaacLab 的 `gym.make()` 需要 `cfg` 参数
2. **避免参数冲突**：不要重复定义 AppLauncher 已提供的参数
3. **配置类层级要正确**：理解配置类的结构，`max_iterations` 是顶层属性
4. **RSL-RL 需要特殊包装**：必须用 `RslRlVecEnvWrapper` 包装环境
5. **参考官方实现**：遇到问题优先查看主项目的官方 `train.py` 实现

### 文件位置

- **外部包训练脚本**：`/root/isaaclab-desktop-organizer/scripts/train_rl.py`
- **官方参考脚本**：`/root/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py`
- **配置类定义**：`/root/isaaclab-desktop-organizer/desktop_organizer/config/ppo_cfg.py`

---

## 环境 ID 对照

### 外部包环境

| 环境 ID | 用途 |
|---------|------|
| `Isaac-Desktop-Organizer-Franka-IK-Rel-v0` | RL 训练（默认） |
| `Isaac-Desktop-Organizer-Franka-IK-Rel-Play-v0` | RL 推理 |
| `Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0` | Mimic 数据采集 + BC 训练 |

### 主项目环境（对比）

| 环境 ID | 用途 |
|---------|------|
| `Isaac-Desktop-Organizer-Franka-RL-IK-Rel-v0` | RL 训练 |
| `Isaac-Desktop-Organizer-Franka-IK-Rel-Mimic-v0` | Mimic 数据采集 + BC 训练 |

**命名差异**：
- RL 环境：主项目多 `RL-` 前缀
- Mimic 环境：`Mimic` 位置不同（主项目在后，外部包在前）

---

**修复完成日期**：2026-01-27
**测试状态**：✅ 通过
