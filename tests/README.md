# Desktop Organizer 测试套件

本目录包含用于验证 `isaaclab-desktop-organizer` 包的完整测试脚本。

## 📋 测试列表

| 测试 | 文件 | 需要 Isaac Sim | 预计时间 | 说明 |
|------|------|---------------|---------|------|
| **测试 1** | `test_1_import.py` | ❌ 不需要 | 1 秒 | 包导入和子模块检查 |
| **测试 2** | `test_2_gym_registration.py` | ❌ 不需要 | 1 秒 | Gym 环境 ID 注册验证 |
| **测试 3** | `test_3_rl_env_create.py` | ✅ 需要 | 20-30 秒 | RL 环境创建和运行 |
| **测试 4** | `test_4_mimic_env_create.py` | ✅ 需要 | 20-30 秒 | Mimic 环境创建和 API 验证 |
| **测试 5** | `test_5_assets.py` | ❌ 不需要 | 1 秒 | 资产文件完整性检查 |

## 🚀 快速开始

### 前置条件

```bash
# 1. 确保 Isaac Lab 已安装
cd /path/to/IsaacLab
./isaaclab.sh --install

# 2. 安装本包
cd /root/isaaclab-desktop-organizer
pip install -e .
```

### 运行单个测试

```bash
cd /path/to/IsaacLab

# 测试 1 和 2：不需要 Isaac Sim，可用普通 Python
python /root/isaaclab-desktop-organizer/tests/test_1_import.py
python /root/isaaclab-desktop-organizer/tests/test_2_gym_registration.py

# 测试 3、4、5：需要 Isaac Sim，必须用 isaaclab.sh
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_3_rl_env_create.py
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_4_mimic_env_create.py
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_5_assets.py
```

### 运行所有测试

```bash
cd /path/to/IsaacLab

# 方式 1: 逐个运行（推荐）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_1_import.py
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_2_gym_registration.py
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_3_rl_env_create.py
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_4_mimic_env_create.py
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_5_assets.py

# 方式 2: 使用测试运行器（开发中）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/run_all_tests.py
```

## 📊 测试详细说明

### 测试 1: 包导入测试

**测试内容：**
- 验证 `desktop_organizer` 包可以正确导入
- 检查版本号
- 验证子模块（envs, mdp, config）

**常见错误：**
- `ModuleNotFoundError` → 运行 `pip install -e .`
- 版本号显示错误 → 检查 `__init__.py` 中的 `__version__`

### 测试 2: Gym 环境注册测试

**测试内容：**
- 验证 RL 环境 ID 是否注册
- 验证 Mimic 环境 ID 是否注册
- 检查 entry_point 和配置路径

**常见错误：**
- `UnregisteredEnv` → 检查 `__init__.py` 中的 `gym.register()`
- 配置路径错误 → 检查 kwargs 中的 `env_cfg_entry_point`

### 测试 3: RL 环境创建测试

**测试内容：**
- 创建 2 个并行 RL 环境
- 检查观测空间和动作空间
- 测试 `reset()` 和 `step()`

**常见错误：**
- `ModuleNotFoundError: omni.log` → 必须用 `./isaaclab.sh -p` 运行
- `FileNotFoundError: table_clean.usd` → 检查 assets 目录
- 导入错误 → 检查 `rl_env_cfg.py` 中的自定义 MDP 导入

### 测试 4: Mimic 环境创建测试

**测试内容：**
- 创建 2 个并行 Mimic 环境
- 验证 Mimic API 实现
- 检查子任务配置

**常见错误：**
- `AttributeError: get_subtask_configs` → 检查 `mimic_env.py` 的实现
- `FileNotFoundError: bc.json` → 检查 config/robomimic/ 目录

### 测试 5: 资产文件检查

**测试内容：**
- 检查 USD 场景文件是否存在
- 检查 BC 配置文件格式
- 验证所有环境配置文件

**常见错误：**
- 文件不存在 → 从原始项目复制 assets 目录
- JSON 格式错误 → 用 JSON 验证器检查 bc.json

## 🔍 排查指南

### 问题：测试 1 失败

```bash
# 解决方案
cd /root/isaaclab-desktop-organizer
pip install -e .

# 验证安装
pip show isaaclab-desktop-organizer
```

### 问题：测试 3/4 报 omni.log 错误

```bash
# 错误：用了普通 python
python test_3_rl_env_create.py  # ❌

# 正确：用 isaaclab.sh
cd /path/to/IsaacLab
./isaaclab.sh -p /root/isaaclab-desktop-organizer/tests/test_3_rl_env_create.py  # ✅
```

### 问题：USD 文件找不到

```bash
# 检查文件是否存在
ls -lh /root/isaaclab-desktop-organizer/assets/scenes/Collected_table_clean/table_clean.usd

# 如果不存在，从原始项目复制
cp -r /path/to/original/assets /root/isaaclab-desktop-organizer/
```

### 问题：自定义 MDP 函数导入失败

```bash
# 检查 mdp/__init__.py 是否正确导出
cat /root/isaaclab-desktop-organizer/desktop_organizer/mdp/__init__.py

# 应该包含：
# from .rewards import object_command_progress, gripper_closed_at_goal
```

## 📝 添加新测试

创建新测试文件时，请遵循以下模板：

```python
"""
测试 X: 测试标题
==================

目的：
    简要说明测试目的

测试内容：
    1. 步骤 1
    2. 步骤 2

预期结果：
    ✅ 预期结果描述

常见错误：
    ❌ 错误 1
       → 解决方案
"""

import sys
import traceback

def test_xxx():
    print("=" * 70)
    print("测试 X: 测试标题")
    print("=" * 70)

    # 测试代码...

    return True

if __name__ == "__main__":
    try:
        success = test_xxx()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)
```

## 📞 获取帮助

如果测试失败且无法解决，请：

1. 查看测试脚本中的 "常见错误" 部分
2. 检查 `/root/isaaclab-desktop-organizer/README.md` 的 FAQ
3. 在 GitHub Issues 中搜索类似问题
4. 提交新的 Issue，附上完整的错误输出
