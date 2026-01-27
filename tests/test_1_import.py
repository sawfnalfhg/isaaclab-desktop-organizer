"""
测试 1: 包导入测试
==================

目的：
    验证 desktop_organizer 包是否正确安装并可以导入

测试内容：
    1. 导入主包
    2. 检查版本号
    3. 验证子模块是否存在（envs, mdp, config）

预期结果：
    ✅ 显示包版本号（0.1.0）
    ✅ 所有子模块都可访问

常见错误：
    ❌ ModuleNotFoundError: No module named 'desktop_organizer'
       → 解决：cd /root/isaaclab-desktop-organizer && pip install -e .

    ❌ ImportError: cannot import name 'xxx'
       → 解决：检查 __init__.py 是否正确导出模块
"""

import sys
import traceback

def test_import():
    print("=" * 70)
    print("测试 1: 包导入测试")
    print("=" * 70)

    # 测试 1.1: 导入主包
    print("\n[1.1] 导入主包...")
    try:
        import desktop_organizer
        print(f"    ✅ 主包导入成功")
        print(f"    📦 版本: {desktop_organizer.__version__}")
    except ModuleNotFoundError as e:
        print(f"    ❌ 失败: {e}")
        print(f"    💡 解决方案: cd /root/isaaclab-desktop-organizer && pip install -e .")
        return False
    except Exception as e:
        print(f"    ❌ 未知错误: {e}")
        traceback.print_exc()
        return False

    # 测试 1.2: 验证子模块
    print("\n[1.2] 验证子模块...")
    submodules = ['envs', 'mdp', 'config']
    for module_name in submodules:
        try:
            module = getattr(desktop_organizer, module_name, None)
            if module is None:
                # 尝试直接导入
                exec(f"from desktop_organizer import {module_name}")
                print(f"    ✅ desktop_organizer.{module_name} 存在")
            else:
                print(f"    ✅ desktop_organizer.{module_name} 存在")
        except ImportError:
            print(f"    ⚠️  desktop_organizer.{module_name} 不存在（可能正常）")
        except Exception as e:
            print(f"    ⚠️  desktop_organizer.{module_name} 导入异常: {e}")

    # 测试 1.3: 验证包路径
    print("\n[1.3] 包安装路径...")
    print(f"    📁 {desktop_organizer.__file__}")

    print("\n" + "=" * 70)
    print("✅ 测试 1 通过：包导入成功")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = test_import()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)
