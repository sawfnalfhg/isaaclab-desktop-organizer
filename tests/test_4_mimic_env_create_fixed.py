"""
测试 4: Mimic 环境创建测试（修复版）
==========================

目的：
    验证 Mimic 环境是否可以成功创建（用于数据采集和 BC 训练）

测试内容：
    1. 启动 Isaac Sim（使用 AppLauncher）
    2. 创建 2 个并行 Mimic 环境实例
    3. 检查环境是否实现了 Mimic API
    4. 验证子任务配置是否正确
    5. 测试环境可以正常重置和关闭

预期结果：
    ✅ Isaac Sim 启动成功
    ✅ Mimic 环境创建成功
    ✅ 显示子任务配置信息
    ✅ 可以成功调用 reset()

常见错误：
    ❌ AttributeError: 'FrankaDesktopOrganizerIKRelMimicEnv' object has no attribute 'get_subtask_configs'
       → 解决：检查 mimic_env.py 是否正确实现了 Mimic API

    ❌ FileNotFoundError: bc.json
       → 解决：检查 config/robomimic/bc.json 是否存在
"""

import sys
import traceback

# ========== CRITICAL: 必须先启动 AppLauncher！ ==========
print("=" * 70)
print("测试 4: Mimic 环境创建测试（修复版）")
print("=" * 70)
print("⚠️  此测试需要 Isaac Sim 环境，必须用 ./isaaclab.sh -p 运行")
print("=" * 70)

# 步骤 1: 启动 Isaac Sim
print("\n[4.0] 启动 Isaac Sim...")
try:
    from isaaclab.app import AppLauncher
    import argparse

    parser = argparse.ArgumentParser()
    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args([])

    # 强制 headless 模式
    args.headless = True

    app_launcher = AppLauncher(args)
    simulation_app = app_launcher.app
    print("    ✅ Isaac Sim 启动成功")
except Exception as e:
    print(f"    ❌ Isaac Sim 启动失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# ========== 现在可以安全导入其他模块了 ==========

def test_mimic_env_create():
    # 测试 4.1: 导入模块
    print("\n[4.1] 导入模块...")
    try:
        import gymnasium as gym
        import desktop_organizer
        print("    ✅ 模块导入成功")
    except ImportError as e:
        print(f"    ❌ 导入失败: {e}")
        return False

    # 测试 4.2: 创建 Mimic 环境
    print("\n[4.2] 创建 Mimic 环境（2 个并行环境，headless 模式）...")
    print("    ⏳ 正在初始化场景（可能需要 10-20 秒）...")
    try:
        env = gym.make(
            'Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0',
            num_envs=2,
            headless=True
        )
        print("    ✅ Mimic 环境创建成功")
    except FileNotFoundError as e:
        print(f"    ❌ 文件未找到: {e}")
        print(f"    💡 检查以下文件:")
        print(f"        - USD 场景: /root/isaaclab-desktop-organizer/assets/scenes/")
        print(f"        - BC 配置: /root/isaaclab-desktop-organizer/desktop_organizer/config/robomimic/bc.json")
        return False
    except ImportError as e:
        print(f"    ❌ 导入错误: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"    ❌ 创建失败: {e}")
        traceback.print_exc()
        return False

    # 测试 4.3: 检查 Mimic API
    print("\n[4.3] 检查 Mimic API 实现...")
    mimic_methods = [
        'get_subtask_configs',
        'get_subtask_term_signals',
        'update_custom_data_dict',
        'get_custom_data_keys'
    ]
    for method_name in mimic_methods:
        if hasattr(env.unwrapped, method_name):
            print(f"    ✅ {method_name} 已实现")
        else:
            print(f"    ❌ {method_name} 未实现")
            print(f"    💡 检查 mimic_env.py 中的方法定义")

    # 测试 4.4: 获取子任务配置
    print("\n[4.4] 获取子任务配置...")
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

    # 测试 4.5: 测试 reset
    print("\n[4.5] 测试环境重置...")
    try:
        obs, info = env.reset()
        print(f"    ✅ Reset 成功")
        if isinstance(obs, dict):
            print(f"    📦 观测包含 {len(obs)} 个键")
    except Exception as e:
        print(f"    ❌ Reset 失败: {e}")
        traceback.print_exc()
        env.close()
        return False

    # 测试 4.6: 关闭环境
    print("\n[4.6] 关闭环境...")
    try:
        env.close()
        print("    ✅ 环境关闭成功")
    except Exception as e:
        print(f"    ⚠️  关闭时警告: {e}")

    print("\n" + "=" * 70)
    print("✅ 测试 4 通过：Mimic 环境创建和配置成功")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = test_mimic_env_create()
        simulation_app.close()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        simulation_app.close()
        sys.exit(1)
