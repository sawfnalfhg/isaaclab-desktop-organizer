"""最小测试：验证 Isaac Sim 是否正确加载"""

print("[Step 1] 测试 omni.log 是否可用...")
try:
    import omni.log
    print("✅ omni.log 可以导入 - Isaac Sim 已加载")
except ImportError as e:
    print(f"❌ omni.log 无法导入: {e}")
    print("💡 Isaac Sim 未正确加载")
    import sys
    sys.exit(1)

print("\n[Step 2] 测试 isaaclab.sim 是否可用...")
try:
    import isaaclab.sim as sim_utils
    print("✅ isaaclab.sim 可以导入")
except ImportError as e:
    print(f"❌ isaaclab.sim 无法导入: {e}")
    import sys
    sys.exit(1)

print("\n[Step 3] 测试 desktop_organizer 包...")
try:
    import desktop_organizer
    print(f"✅ desktop_organizer 可以导入 (版本 {desktop_organizer.__version__})")
except ImportError as e:
    print(f"❌ desktop_organizer 无法导入: {e}")
    import sys
    sys.exit(1)

print("\n✅ 所有基础模块导入成功！")
print("💡 问题不在 Isaac Sim 加载，而在环境创建时")
