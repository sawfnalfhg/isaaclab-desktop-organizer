# 🔍 Desktop Organizer 测试问题完整解决方案

## 问题总结

在运行外部包 `desktop_organizer` 的测试时，遇到了多个问题。本文档详细记录了问题原因和解决方案。

---

## 问题 1: "No module named 'omni.log'"

### 错误现象
```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_3_rl_env_create.py
# 报错：ModuleNotFoundError: No module named 'omni.log'
```

### 根本原因

**错误的导入顺序**！原测试脚本直接导入了 `gymnasium` 并调用 `gym.make()`，但此时 **Isaac Sim 还没有启动**。

```python
# ❌ 错误的方式（原测试脚本）
import gymnasium as gym  # Isaac Sim 未启动
import desktop_organizer
env = gym.make(...)  # 💥 报错！
```

**正确的方式**（参考主项目）：

```python
# ✅ 正确的方式
# 1. 先启动 AppLauncher
from isaaclab.app import AppLauncher
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 2. 然后才导入其他模块
import gymnasium as gym
import desktop_organizer
env = gym.make(...)  # 正常工作！
```

### 关键认知

`./isaaclab.sh -p script.py` 只是：
- ✅ 设置环境变量（`LD_LIBRARY_PATH`、`PYTHONPATH` 等）
- ❌ **不会自动启动 Isaac Sim**

**必须在脚本中显式调用 `AppLauncher`** 才能启动 Isaac Sim。

---

## 问题 2: "ManagerBasedRLEnv.__init__() missing 1 required positional argument: 'cfg'"

### 错误现象
```python
env = gym.make('Isaac-Desktop-Organizer-Franka-IK-Rel-v0', num_envs=2, headless=True)
# TypeError: ManagerBasedRLEnv.__init__() missing 1 required positional argument: 'cfg'
```

### 根本原因

`gym.make()` **缺少必需的 `cfg` 参数**。

### 解决方案

参考主项目 `scripts/reinforcement_learning/rsl_rl/train.py` 第 155 行：

```python
# ❌ 错误方式
env = gym.make(task_name, num_envs=2, headless=True)

# ✅ 正确方式（参考主项目）
from isaaclab_tasks.utils import parse_env_cfg

env_cfg = parse_env_cfg(
    task_name="Isaac-Desktop-Organizer-Franka-IK-Rel-v0",
    device="cpu",
    num_envs=2,
)

env = gym.make("Isaac-Desktop-Organizer-Franka-IK-Rel-v0", cfg=env_cfg)
```

---

## 问题 3: "'numpy.ndarray' object has no attribute 'to'"

### 错误现象
```python
action = env.action_space.sample()  # 返回 numpy array
env.step(action)  # 报错：numpy.ndarray 没有 'to' 方法
```

### 根本原因

IsaacLab 期望动作是 **torch.Tensor**，但 `action_space.sample()` 返回的是 **numpy.ndarray**。

### 解决方案

```python
import torch

# ❌ 错误方式
action = env.action_space.sample()  # numpy array
env.step(action)  # 报错！

# ✅ 正确方式
action = env.action_space.sample()
action_tensor = torch.tensor(action, device="cpu", dtype=torch.float32)
env.step(action_tensor)  # 正常工作！
```

---

## 完整的正确测试脚本模板

基于主项目 `desktop_organizer_rl` 的实现：

```python
"""RL 环境测试脚本（参考主项目实现）"""

import sys
import traceback

# ========== 1. 启动 AppLauncher（必须在最前面！） ==========
from isaaclab.app import AppLauncher
import argparse

parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args([])
args.headless = True

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# ========== 2. 导入模块（在 AppLauncher 之后！） ==========
import gymnasium as gym
import torch
import desktop_organizer
from isaaclab_tasks.utils import parse_env_cfg

# ========== 3. 解析环境配置 ==========
env_cfg = parse_env_cfg(
    task_name="Isaac-Desktop-Organizer-Franka-IK-Rel-v0",
    device="cpu",
    num_envs=2,
)

# ========== 4. 创建环境（必须传递 cfg！） ==========
env = gym.make("Isaac-Desktop-Organizer-Franka-IK-Rel-v0", cfg=env_cfg)

# ========== 5. 测试环境 ==========
obs, info = env.reset()

action = env.action_space.sample()
action_tensor = torch.tensor(action, device="cpu", dtype=torch.float32)  # 转换！
obs, reward, terminated, truncated, info = env.step(action_tensor)

# ========== 6. 关闭 ==========
env.close()
simulation_app.close()
```

---

## 主项目 vs 外部包的对比

| 项目 | 主项目 | 外部包 |
|------|--------|--------|
| **位置** | `source/isaaclab_tasks/.../desktop_organizer_rl/` | `/root/isaaclab-desktop-organizer/` |
| **环境 ID** | `Isaac-Desktop-Organizer-Franka-RL-v0` | `Isaac-Desktop-Organizer-Franka-IK-Rel-v0` |
| **注册方式** | ✅ 完全相同 | ✅ 完全相同 |
| **配置类** | `DesktopOrganizerRLEnvCfg` | `FrankaDesktopOrganizerIKRelEnvCfg` |
| **使用方式** | 官方脚本 + `--task` 参数 | 独立脚本或测试 |

**关键差异**：
- 主项目通过 `isaaclab_tasks` 自动加载
- 外部包需要显式 `import desktop_organizer`

---

## 参考代码位置

### 主项目的正确实现

| 文件 | 关键代码行 | 说明 |
|------|----------|------|
| `scripts/reinforcement_learning/rsl_rl/train.py` | 行 49-50 | 启动 AppLauncher |
| `scripts/reinforcement_learning/rsl_rl/train.py` | 行 76-82 | 导入模块（在 AppLauncher 之后） |
| `scripts/reinforcement_learning/rsl_rl/train.py` | 行 108-109 | 使用 Hydra 解析配置 |
| `scripts/reinforcement_learning/rsl_rl/train.py` | 行 155 | `gym.make(task, cfg=env_cfg)` |

### 外部包的文件

| 文件 | 用途 |
|------|------|
| `/root/isaaclab-desktop-organizer/desktop_organizer/__init__.py` | Gym 环境注册 |
| `/root/isaaclab-desktop-organizer/desktop_organizer/envs/rl_env_cfg.py` | RL 环境配置 |
| `/root/isaaclab-desktop-organizer/tests/test_3_FINAL.py` | 正确的测试脚本 |

---

## 最终测试命令

```bash
cd /root/IsaacLab

# 运行修复后的测试
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_3_FINAL.py
```

**预期输出**：
```
✅ Isaac Sim 启动成功
✅ 模块导入成功
✅ 环境配置解析成功
✅ 环境创建成功
✅ Reset 成功
✅ Step 成功
✅ 环境关闭成功
✅ 测试 3 通过：RL 环境创建和运行成功
```

---

## 关键学习点总结

1. **AppLauncher 必须最先调用**
   - 在导入 `gymnasium`、`torch` 等之前
   - 在任何 Isaac Sim 相关操作之前

2. **gym.make() 必须传递 cfg**
   - 使用 `parse_env_cfg()` 解析配置
   - 传递 `cfg=env_cfg` 参数

3. **动作必须是 torch.Tensor**
   - 不能直接使用 `action_space.sample()` 的结果
   - 必须转换为 `torch.tensor()`

4. **参考主项目的实现**
   - IsaacLab 有标准的启动模式
   - 所有涉及仿真的脚本都遵循相同模式

---

## 下一步

测试脚本 `/root/isaaclab-desktop-organizer/tests/test_3_FINAL.py` 已经修复了所有问题，应该可以正常运行。

如果还有问题，请检查：
1. USD 场景文件是否存在
2. 自定义 MDP 函数是否正确导出
3. BC 配置文件是否存在（Mimic 环境需要）
