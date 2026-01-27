"""
测试 5: 资产文件检查
====================

目的：
    验证所有必需的资产文件是否存在且可访问

测试内容：
    1. 检查 USD 场景文件
    2. 检查 Robomimic BC 配置文件
    3. 验证文件路径解析正确

预期结果：
    ✅ 所有资产文件存在
    ✅ 文件大小合理
    ✅ JSON 文件格式正确

常见错误：
    ❌ FileNotFoundError: table_clean.usd
       → 解决：检查 assets/scenes/Collected_table_clean/ 目录

    ❌ FileNotFoundError: bc.json
       → 解决：检查 desktop_organizer/config/robomimic/ 目录

    ❌ json.JSONDecodeError
       → 解决：检查 bc.json 文件格式是否正确
"""

import sys
import traceback
import json
from pathlib import Path

def test_assets():
    print("=" * 70)
    print("测试 5: 资产文件检查")
    print("=" * 70)

    # 获取包根目录
    try:
        import desktop_organizer
        pkg_dir = Path(desktop_organizer.__file__).parent.parent
        print(f"\n📁 包根目录: {pkg_dir}")
    except ImportError:
        print("❌ 无法导入 desktop_organizer 包")
        return False

    all_checks_passed = True

    # 测试 5.1: USD 场景文件
    print("\n[5.1] 检查 USD 场景文件...")
    usd_path = pkg_dir / "assets" / "scenes" / "Collected_table_clean" / "table_clean.usd"
    if usd_path.exists():
        size_kb = usd_path.stat().st_size / 1024
        print(f"    ✅ USD 文件存在: {usd_path}")
        print(f"    📏 文件大小: {size_kb:.2f} KB")
        if size_kb < 10:
            print(f"    ⚠️  文件太小（< 10KB），可能损坏")
            all_checks_passed = False
    else:
        print(f"    ❌ USD 文件不存在: {usd_path}")
        print(f"    💡 确保从原始项目复制了 assets 目录")
        all_checks_passed = False

    # 测试 5.2: Robomimic BC 配置
    print("\n[5.2] 检查 Robomimic BC 配置...")
    bc_json_path = pkg_dir / "desktop_organizer" / "config" / "robomimic" / "bc.json"
    if bc_json_path.exists():
        print(f"    ✅ BC 配置存在: {bc_json_path}")
        try:
            with open(bc_json_path, 'r') as f:
                bc_config = json.load(f)
            print(f"    ✅ JSON 格式正确")
            print(f"    📋 配置包含 {len(bc_config)} 个顶级键")

            # 检查关键配置项
            if 'train' in bc_config:
                print(f"    ✅ 包含 train 配置")
            if 'observation' in bc_config:
                obs_keys = bc_config['observation'].get('modalities', {}).get('obs', {}).get('low_dim', [])
                print(f"    📊 观测键数量: {len(obs_keys)}")
                if len(obs_keys) > 0:
                    print(f"        示例: {', '.join(obs_keys[:3])}")
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON 格式错误: {e}")
            all_checks_passed = False
        except Exception as e:
            print(f"    ⚠️  读取配置时出错: {e}")
    else:
        print(f"    ❌ BC 配置不存在: {bc_json_path}")
        all_checks_passed = False

    # 测试 5.3: PPO 配置
    print("\n[5.3] 检查 PPO 配置...")
    ppo_cfg_path = pkg_dir / "desktop_organizer" / "config" / "ppo_cfg.py"
    if ppo_cfg_path.exists():
        print(f"    ✅ PPO 配置存在: {ppo_cfg_path}")
    else:
        print(f"    ⚠️  PPO 配置不存在（可能正常）")

    # 测试 5.4: 环境配置文件
    print("\n[5.4] 检查环境配置文件...")
    env_configs = [
        ("RL 环境配置", "desktop_organizer/envs/rl_env_cfg.py"),
        ("Mimic 环境配置", "desktop_organizer/envs/mimic_env_cfg.py"),
        ("Mimic 环境包装器", "desktop_organizer/envs/mimic_env.py"),
    ]

    for name, rel_path in env_configs:
        path = pkg_dir / rel_path
        if path.exists():
            print(f"    ✅ {name}: {path.name}")
        else:
            print(f"    ❌ {name} 不存在: {rel_path}")
            all_checks_passed = False

    # 测试 5.5: MDP 模块
    print("\n[5.5] 检查 MDP 模块...")
    mdp_path = pkg_dir / "desktop_organizer" / "mdp" / "rewards.py"
    if mdp_path.exists():
        print(f"    ✅ 自定义奖励函数: {mdp_path}")
        # 尝试读取并统计函数数量
        try:
            with open(mdp_path, 'r') as f:
                content = f.read()
                func_count = content.count('def ')
                print(f"    📊 定义了约 {func_count} 个函数")
        except Exception:
            pass
    else:
        print(f"    ❌ 奖励函数文件不存在: {mdp_path}")
        all_checks_passed = False

    # 测试 5.6: 训练脚本
    print("\n[5.6] 检查训练脚本...")
    scripts = [
        ("RL 训练脚本", "scripts/train_rl.py"),
        ("RL 评估脚本", "scripts/play_rl.py"),
    ]

    for name, rel_path in scripts:
        path = pkg_dir / rel_path
        if path.exists():
            print(f"    ✅ {name}: {path.name}")
        else:
            print(f"    ⚠️  {name} 不存在（可选）")

    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✅ 测试 5 通过：所有必需资产文件存在")
    else:
        print("⚠️  测试 5 部分通过：部分资产文件缺失或有问题")
    print("=" * 70)
    return all_checks_passed

if __name__ == "__main__":
    try:
        success = test_assets()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)
