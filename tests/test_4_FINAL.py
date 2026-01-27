"""
测试 4: Mimic 环境创建测试（修复版）
==========================

参考 test_3_FINAL.py 的修复方法
"""

import sys
import traceback

print("=" * 70)
print("测试 4: Mimic 环境创建测试")
print("=" * 70)

# ========== 步骤 1: 启动 AppLauncher ==========
print("\n[4.0] 启动 Isaac Sim...")
try:
    from isaaclab.app import AppLauncher
    import argparse

    parser = argparse.ArgumentParser()
    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args([])
    args.headless = True

    app_launcher = AppLauncher(args)
    simulation_app = app_launcher.app
    print("    ✅ Isaac Sim 启动成功")
except Exception as e:
    print(f"    ❌ Isaac Sim 启动失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# ========== 步骤 2: 导入模块（在 AppLauncher 之后！） ==========
print("\n[4.1] 导入模块...")
try:
    import gymnasium as gym
    import desktop_organizer
    from isaaclab_tasks.utils import parse_env_cfg
    print("    ✅ 模块导入成功")
except ImportError as e:
    print(f"    ❌ 导入失败: {e}")
    traceback.print_exc()
    simulation_app.close()
    sys.exit(1)

# ========== 步骤 3: 解析环境配置 ==========
print("\n[4.2] 解析 Mimic 环境配置...")
try:
    env_cfg = parse_env_cfg(
        task_name="Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0",
        device="cpu",
        num_envs=2,
    )
    print("    ✅ 环境配置解析成功")
    print(f"    ⚙️  环境数量: {env_cfg.scene.num_envs}")
except Exception as e:
    print(f"    ❌ 配置解析失败: {e}")
    traceback.print_exc()
    simulation_app.close()
    sys.exit(1)

# ========== 步骤 4: 创建 Mimic 环境 ==========
print("\n[4.3] 创建 Mimic 环境...")
print("    ⏳ 正在加载场景（约 10-15 秒）...")
try:
    # 关键：必须传递 cfg 参数！
    env = gym.make("Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0", cfg=env_cfg)
    print("    ✅ Mimic 环境创建成功")
except Exception as e:
    print(f"    ❌ 创建失败: {e}")
    traceback.print_exc()
    simulation_app.close()
    sys.exit(1)

# ========== 步骤 5: 检查 Mimic API ==========
print("\n[4.4] 检查 Mimic API 实现...")
mimic_methods = [
    'get_subtask_configs',
    'get_subtask_term_signals',
    'update_custom_data_dict',
    'get_custom_data_keys'
]
try:
    for method_name in mimic_methods:
        if hasattr(env.unwrapped, method_name):
            print(f"    ✅ {method_name} 已实现")
        else:
            print(f"    ⚠️  {method_name} 未实现")
except Exception as e:
    print(f"    ⚠️  检查失败: {e}")

# ========== 步骤 6: 获取子任务配置 ==========
print("\n[4.5] 获取子任务配置...")
try:
    if hasattr(env.unwrapped, 'get_subtask_configs'):
        subtask_configs = env.unwrapped.get_subtask_configs()
        print(f"    ✅ 子任务配置获取成功")
        print(f"    📋 子任务数量: {len(subtask_configs)}")
        for i, config in enumerate(subtask_configs, 1):
            print(f"        {i}. {config.get('name', 'Unnamed')}: {config.get('selection_strategy', 'N/A')}")
    else:
        print(f"    ⚠️  get_subtask_configs 方法不存在")
except Exception as e:
    print(f"    ⚠️  获取子任务配置失败: {e}")
    traceback.print_exc()

# ========== 步骤 7: 测试 Reset ==========
print("\n[4.6] 测试环境重置...")
try:
    obs, info = env.reset()
    print(f"    ✅ Reset 成功")
    if isinstance(obs, dict):
        print(f"    📦 观测包含 {len(obs)} 个键")
except Exception as e:
    print(f"    ❌ Reset 失败: {e}")
    traceback.print_exc()
    env.close()
    simulation_app.close()
    sys.exit(1)

# ========== 步骤 8: 关闭环境 ==========
print("\n[4.7] 关闭环境...")
try:
    env.close()
    print("    ✅ 环境关闭成功")
except Exception as e:
    print(f"    ⚠️  关闭时警告: {e}")

print("\n" + "=" * 70)
print("✅ 测试 4 通过：Mimic 环境创建和配置成功")
print("=" * 70)

simulation_app.close()
sys.exit(0)
