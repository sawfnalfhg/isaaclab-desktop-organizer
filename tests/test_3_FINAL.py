"""
测试 3: RL 环境创建测试
=================

参考主项目 desktop_organizer_rl 的实现方式
"""

import sys
import traceback

print("=" * 70)
print("测试 3: RL 环境创建测试")
print("=" * 70)

# ========== 步骤 1: 启动 AppLauncher ==========
print("\n[3.0] 启动 Isaac Sim...")
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
    simulation_app.close()
    sys.exit(1)

# ========== 步骤 3: 解析环境配置 ==========
print("\n[3.2] 解析环境配置...")
try:
    env_cfg = parse_env_cfg(
        task_name="Isaac-Desktop-Organizer-Franka-IK-Rel-v0",
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

# ========== 步骤 4: 创建环境 ==========
print("\n[3.3] 创建 RL 环境...")
print("    ⏳ 正在加载场景（约 10-15 秒）...")
try:
    # 关键：必须传递 cfg 参数！
    env = gym.make("Isaac-Desktop-Organizer-Franka-IK-Rel-v0", cfg=env_cfg)
    print("    ✅ 环境创建成功")
except Exception as e:
    print(f"    ❌ 创建失败: {e}")
    traceback.print_exc()
    simulation_app.close()
    sys.exit(1)

# ========== 步骤 5: 检查空间 ==========
print("\n[3.4] 检查观测和动作空间...")
try:
    obs_space = env.observation_space
    action_space = env.action_space
    print(f"    ✅ 观测空间: {type(obs_space).__name__}")
    print(f"    ✅ 动作空间: {action_space}")
except Exception as e:
    print(f"    ⚠️  检查失败: {e}")

# ========== 步骤 6: 测试 Reset ==========
print("\n[3.5] 测试环境重置...")
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

# ========== 步骤 7: 测试 Step ==========
print("\n[3.6] 测试单步执行...")
try:
    action = env.action_space.sample()
    # 关键：转换为 torch tensor
    action_tensor = torch.tensor(action, device="cpu", dtype=torch.float32)
    obs, reward, terminated, truncated, info = env.step(action_tensor)
    print(f"    ✅ Step 成功")
    print(f"    🎁 平均奖励: {reward.mean().item():.2f}")
except Exception as e:
    print(f"    ❌ Step 失败: {e}")
    traceback.print_exc()
    env.close()
    simulation_app.close()
    sys.exit(1)

# ========== 步骤 8: 关闭环境 ==========
print("\n[3.7] 关闭环境...")
try:
    env.close()
    print("    ✅ 环境关闭成功")
except Exception as e:
    print(f"    ⚠️  关闭时警告: {e}")

print("\n" + "=" * 70)
print("✅ 测试 3 通过：RL 环境创建和运行成功")
print("=" * 70)

simulation_app.close()
sys.exit(0)
