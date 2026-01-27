"""
测试 3: RL 环境创建测试（完全修复版）
=======================

使用 IsaacLab 官方的环境创建工具 + 正确处理 action
"""

import sys
import traceback

# ========== CRITICAL: 必须先启动 AppLauncher！ ==========
print("=" * 70)
print("测试 3: RL 环境创建测试（完全修复版）")
print("=" * 70)
print("⚠️  此测试需要 Isaac Sim 环境，必须用 ./isaaclab.sh -p 运行")
print("=" * 70)

# 步骤 1: 启动 Isaac Sim
print("\n[3.0] 启动 Isaac Sim...")
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

def test_rl_env_create():
    # 测试 3.1: 导入模块
    print("\n[3.1] 导入模块...")
    try:
        import gymnasium as gym
        import torch
        import desktop_organizer
        from isaaclab_tasks.utils import parse_env_cfg
        print("    ✅ 模块导入成功")
    except ImportError as e:
        print(f"    ❌ 导入失败: {e}")
        traceback.print_exc()
        return False

    # 测试 3.2: 解析环境配置
    print("\n[3.2] 解析环境配置...")
    try:
        env_cfg = parse_env_cfg(
            task_name="Isaac-Desktop-Organizer-Franka-IK-Rel-v0",
            device="cpu",
            num_envs=2,
            use_fabric=False,
        )
        print("    ✅ 环境配置解析成功")
        print(f"    ⚙️  环境数量: {env_cfg.scene.num_envs}")
    except Exception as e:
        print(f"    ❌ 配置解析失败: {e}")
        traceback.print_exc()
        return False

    # 测试 3.3: 创建环境
    print("\n[3.3] 创建 RL 环境...")
    print("    ⏳ 正在初始化场景（可能需要 10-20 秒）...")
    try:
        env = gym.make("Isaac-Desktop-Organizer-Franka-IK-Rel-v0", cfg=env_cfg)
        print("    ✅ 环境创建成功")
    except FileNotFoundError as e:
        print(f"    ❌ 文件未找到: {e}")
        print(f"    💡 检查 USD 场景文件: /root/isaaclab-desktop-organizer/assets/scenes/")
        traceback.print_exc()
        return False
    except ImportError as e:
        print(f"    ❌ 导入错误: {e}")
        print(f"    💡 检查 desktop_organizer/envs/rl_env_cfg.py 中的 import 语句")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"    ❌ 创建失败: {e}")
        traceback.print_exc()
        return False

    # 测试 3.4: 检查观测空间
    print("\n[3.4] 检查观测空间...")
    try:
        obs_space = env.observation_space
        print(f"    ✅ 观测空间类型: {type(obs_space).__name__}")
        if hasattr(obs_space, 'spaces'):
            print(f"    📊 观测空间包含 {len(obs_space.spaces)} 个键:")
            for key, space in list(obs_space.spaces.items())[:5]:
                print(f"        - {key}: {space}")
            if len(obs_space.spaces) > 5:
                print(f"        ... 还有 {len(obs_space.spaces) - 5} 个观测")
        else:
            print(f"    📊 观测空间: {obs_space}")
    except Exception as e:
        print(f"    ❌ 检查失败: {e}")
        traceback.print_exc()

    # 测试 3.5: 检查动作空间
    print("\n[3.5] 检查动作空间...")
    try:
        action_space = env.action_space
        print(f"    ✅ 动作空间类型: {type(action_space).__name__}")
        print(f"    📊 动作空间: {action_space}")
        if hasattr(action_space, 'shape'):
            print(f"    📏 动作维度: {action_space.shape}")
    except Exception as e:
        print(f"    ❌ 检查失败: {e}")
        traceback.print_exc()

    # 测试 3.6: 测试 reset
    print("\n[3.6] 测试环境重置...")
    try:
        obs, info = env.reset()
        print(f"    ✅ Reset 成功")
        if isinstance(obs, dict):
            print(f"    📦 观测包含 {len(obs)} 个键")
            for key in list(obs.keys())[:3]:
                print(f"        - {key}: shape {obs[key].shape}")
        print(f"    ℹ️  Info 包含 {len(info)} 个键")
    except Exception as e:
        print(f"    ❌ Reset 失败: {e}")
        traceback.print_exc()
        env.close()
        return False

    # 测试 3.7: 测试单步执行
    print("\n[3.7] 测试单步执行...")
    try:
        action = env.action_space.sample()
        # 转换为 torch tensor
        action_tensor = torch.tensor(action, device="cpu", dtype=torch.float32)
        obs, reward, terminated, truncated, info = env.step(action_tensor)
        print(f"    ✅ Step 成功")
        print(f"    🎁 Reward shape: {reward.shape}")
        print(f"    🏁 Terminated: {terminated.sum().item()}/{len(terminated)} 环境")
        print(f"    ⏱️  Truncated: {truncated.sum().item()}/{len(truncated)} 环境")
    except Exception as e:
        print(f"    ❌ Step 失败: {e}")
        traceback.print_exc()
        env.close()
        return False

    # 测试 3.8: 关闭环境
    print("\n[3.8] 关闭环境...")
    try:
        env.close()
        print("    ✅ 环境关闭成功")
    except Exception as e:
        print(f"    ⚠️  关闭时警告: {e}")

    print("\n" + "=" * 70)
    print("✅ 测试 3 通过：RL 环境创建和运行成功")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = test_rl_env_create()
        simulation_app.close()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        try:
            simulation_app.close()
        except:
            pass
        sys.exit(1)
