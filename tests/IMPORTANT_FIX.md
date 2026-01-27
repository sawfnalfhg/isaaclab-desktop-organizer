# 🔴 重要修复：测试 3 和 4 的问题解决方案

## 问题原因

原始的测试 3 和 4 脚本**缺少关键步骤**：在导入 `gymnasium` 之前，**必须先启动 Isaac Sim（AppLauncher）**。

### 错误的顺序（原测试脚本）❌
```python
import gymnasium as gym  # ❌ Isaac Sim 还没启动！
import desktop_organizer
env = gym.make('Isaac-Desktop-Organizer-Franka-IK-Rel-v0')  # 报错: No module named 'omni.log'
```

### 正确的顺序（修复后）✅
```python
from isaaclab.app import AppLauncher
app_launcher = AppLauncher(args)  # ✅ 先启动 Isaac Sim
simulation_app = app_launcher.app

import gymnasium as gym  # ✅ 然后才导入 gymnasium
import desktop_organizer
env = gym.make('Isaac-Desktop-Organizer-Franka-IK-Rel-v0')  # 正常工作！
```

---

## 🚀 立即使用修复版测试

### 测试 3：RL 环境创建（修复版）
```bash
cd /root/IsaacLab
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_3_rl_env_create_fixed.py
```

### 测试 4：Mimic 环境创建（修复版）
```bash
cd /root/IsaacLab
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_4_mimic_env_create_fixed.py
```

---

## 📋 文件对比

| 文件 | 状态 | 说明 |
|------|------|------|
| `test_3_rl_env_create.py` | ❌ 有 Bug | 原版本，会报 omni.log 错误 |
| `test_3_rl_env_create_fixed.py` | ✅ 修复 | 正确启动 AppLauncher |
| `test_4_mimic_env_create.py` | ❌ 有 Bug | 原版本，会报 omni.log 错误 |
| `test_4_mimic_env_create_fixed.py` | ✅ 修复 | 正确启动 AppLauncher |

---

## 🔍 为什么 `-p` 参数也不够？

很多人误以为 `./isaaclab.sh -p script.py` 会自动初始化 Isaac Sim，但实际上：

| 运行方式 | Isaac Sim 初始化 | 说明 |
|---------|-----------------|------|
| `python script.py` | ❌ 否 | 普通 Python 环境 |
| `./isaaclab.sh -p -c "code"` | ❌ 否 | 只激活 conda 环境 |
| `./isaaclab.sh -p script.py` | ⚠️ 部分 | 设置环境变量，但不启动 Isaac Sim |
| `./isaaclab.sh -p script_with_AppLauncher.py` | ✅ 是 | 脚本中调用 AppLauncher，完整启动 |

**关键**：`./isaaclab.sh -p` 只是设置了环境变量（`LD_LIBRARY_PATH`、`PYTHONPATH` 等），**并不会自动启动 Isaac Sim**。必须在脚本中显式调用 `AppLauncher`。

---

## 📖 IsaacLab 官方示例的启动模式

查看任何官方训练脚本（如 `scripts/reinforcement_learning/rsl_rl/train.py`），都会看到这个模式：

```python
# 1. 先 parse 参数
from isaaclab.app import AppLauncher
parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# 2. 启动 Isaac Sim（关键步骤！）
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 3. 然后才导入其他模块
import gymnasium as gym
import torch
# ... 其他导入 ...

# 4. 使用环境
env = gym.make('Isaac-Cartpole-v0')
```

这是 **IsaacLab 的标准启动模式**，所有涉及仿真的脚本都必须遵循。

---

## 🎯 下一步

使用修复版测试脚本，应该可以正常创建环境了：

```bash
cd /root/IsaacLab

# 测试 RL 环境
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_3_rl_env_create_fixed.py

# 测试 Mimic 环境
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_4_mimic_env_create_fixed.py
```

如果还有问题，请检查：
1. USD 场景文件是否存在：`ls -lh /root/isaaclab-desktop-organizer/assets/scenes/Collected_table_clean/table_clean.usd`
2. BC 配置文件是否存在：`ls -lh /root/isaaclab-desktop-organizer/desktop_organizer/config/robomimic/bc.json`
3. 自定义 MDP 函数是否正确导出：`cat /root/isaaclab-desktop-organizer/desktop_organizer/mdp/__init__.py`
