#!/bin/bash
# 快速运行所有测试的脚本
# 使用方法: cd /path/to/IsaacLab && bash /root/isaaclab-desktop-organizer/tests/quick_test.sh

set -e  # 遇到错误立即停止

ISAACLAB_DIR="${1:-/root/IsaacLab}"
TEST_DIR="/root/isaaclab-desktop-organizer/tests"

echo "======================================================================"
echo "       Desktop Organizer 快速测试套件"
echo "======================================================================"
echo "IsaacLab 目录: $ISAACLAB_DIR"
echo ""

# 进入 IsaacLab 目录
cd "$ISAACLAB_DIR"

# 测试 1: 包导入（不需要 Isaac Sim）
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 测试 1/5: 包导入测试（1秒）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python "$TEST_DIR/test_1_import.py" || { echo "❌ 测试 1 失败"; exit 1; }

# 测试 2: Gym 注册（不需要 Isaac Sim）
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎮 测试 2/5: Gym 环境注册（1秒）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python "$TEST_DIR/test_2_gym_registration.py" || { echo "❌ 测试 2 失败"; exit 1; }

# 测试 5: 资产检查（不需要 Isaac Sim）
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 测试 5/5: 资产文件检查（1秒）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python "$TEST_DIR/test_5_assets.py" || { echo "❌ 测试 5 失败"; exit 1; }

# 测试 3: RL 环境创建（需要 Isaac Sim）
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 测试 3/5: RL 环境创建（20-30秒）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./isaaclab.sh -p "$TEST_DIR/test_3_rl_env_create.py" || { echo "❌ 测试 3 失败"; exit 1; }

# 测试 4: Mimic 环境创建（需要 Isaac Sim）
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 测试 4/5: Mimic 环境创建（20-30秒）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./isaaclab.sh -p "$TEST_DIR/test_4_mimic_env_create.py" || { echo "❌ 测试 4 失败"; exit 1; }

# 全部完成
echo ""
echo "======================================================================"
echo "✅ 所有测试通过！Package 可以发布到 GitHub"
echo "======================================================================"
echo ""
echo "下一步："
echo "  1. 更新 pyproject.toml 中的作者信息"
echo "  2. 更新 README.md 中的 GitHub URL"
echo "  3. 提交并推送到 GitHub"
echo ""
