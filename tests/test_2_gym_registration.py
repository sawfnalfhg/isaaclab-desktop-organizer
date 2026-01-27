"""
测试 2: Gym 环境注册测试
========================

目的：
    验证环境 ID 是否正确注册到 Gymnasium

测试内容：
    1. 检查 RL 环境 ID 是否注册
    2. 检查 Mimic 环境 ID 是否注册
    3. 验证环境配置是否正确

预期结果：
    ✅ 显示两个环境 ID 都已注册
    ✅ 显示环境的 entry_point 和配置

常见错误：
    ❌ gymnasium.error.UnregisteredEnv: Isaac-Desktop-Organizer-Franka-IK-Rel-v0
       → 解决：检查 desktop_organizer/__init__.py 中的 gym.register() 调用

    ❌ KeyError: 'env_cfg_entry_point'
       → 解决：检查 gym.register() 的 kwargs 参数
"""

import sys
import traceback

def test_gym_registration():
    print("=" * 70)
    print("测试 2: Gym 环境注册测试")
    print("=" * 70)

    # 测试 2.1: 导入必需模块
    print("\n[2.1] 导入模块...")
    try:
        import gymnasium as gym
        import desktop_organizer
        print("    ✅ gymnasium 和 desktop_organizer 导入成功")
    except ImportError as e:
        print(f"    ❌ 导入失败: {e}")
        return False

    # 测试 2.2: 检查 RL 环境注册
    print("\n[2.2] 检查 RL 环境注册...")
    rl_env_id = 'Isaac-Desktop-Organizer-Franka-IK-Rel-v0'
    try:
        env_spec = gym.spec(rl_env_id)
        print(f"    ✅ 环境已注册: {rl_env_id}")
        print(f"    📋 Entry Point: {env_spec.entry_point}")
        if hasattr(env_spec, 'kwargs') and env_spec.kwargs:
            print(f"    ⚙️  Config Entry: {env_spec.kwargs.get('env_cfg_entry_point', 'N/A')}")
    except gym.error.UnregisteredEnv:
        print(f"    ❌ 环境未注册: {rl_env_id}")
        print(f"    💡 检查 desktop_organizer/__init__.py 中的 gym.register()")
        return False
    except Exception as e:
        print(f"    ❌ 错误: {e}")
        traceback.print_exc()
        return False

    # 测试 2.3: 检查 Mimic 环境注册
    print("\n[2.3] 检查 Mimic 环境注册...")
    mimic_env_id = 'Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0'
    try:
        env_spec = gym.spec(mimic_env_id)
        print(f"    ✅ 环境已注册: {mimic_env_id}")
        print(f"    📋 Entry Point: {env_spec.entry_point}")
        if hasattr(env_spec, 'kwargs') and env_spec.kwargs:
            print(f"    ⚙️  Config Entry: {env_spec.kwargs.get('env_cfg_entry_point', 'N/A')}")
            print(f"    🤖 BC Config: {env_spec.kwargs.get('robomimic_bc_cfg_entry_point', 'N/A')}")
    except gym.error.UnregisteredEnv:
        print(f"    ❌ 环境未注册: {mimic_env_id}")
        print(f"    💡 检查 desktop_organizer/__init__.py 中的 gym.register()")
        return False
    except Exception as e:
        print(f"    ❌ 错误: {e}")
        traceback.print_exc()
        return False

    # 测试 2.4: 列出所有 Desktop Organizer 相关环境
    print("\n[2.4] 所有 Desktop Organizer 环境...")
    all_envs = [env_id for env_id in gym.envs.registry.keys() if 'Desktop-Organizer' in env_id]
    for env_id in all_envs:
        print(f"    📌 {env_id}")

    print("\n" + "=" * 70)
    print("✅ 测试 2 通过：Gym 环境注册成功")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = test_gym_registration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)
