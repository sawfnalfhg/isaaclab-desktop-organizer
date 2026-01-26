"""
Smoke test for isaaclab-desktop-organizer package structure.
This test verifies the package structure without requiring Isaac Sim.
"""

import os
import sys


def test_package_structure():
    """Test that all expected files and directories exist."""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    required_files = [
        "setup.py",
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "MANIFEST.in",
        ".gitignore",
        "desktop_organizer/__init__.py",
        "desktop_organizer/envs/__init__.py",
        "desktop_organizer/envs/rl_env_cfg.py",
        "desktop_organizer/envs/mimic_env_cfg.py",
        "desktop_organizer/envs/mimic_env.py",
        "desktop_organizer/mdp/__init__.py",
        "desktop_organizer/mdp/rewards.py",
        "desktop_organizer/config/__init__.py",
        "desktop_organizer/config/ppo_cfg.py",
        "desktop_organizer/config/robomimic/bc.json",
        "desktop_organizer/assets/__init__.py",
        "scripts/train_rl.py",
        "scripts/play_rl.py",
        "scripts/README.md",
        "docs/installation.md",
    ]

    print("=" * 80)
    print("SMOKE TEST: Package Structure Verification")
    print("=" * 80)

    all_passed = True
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("✓ All required files found!")
        print("=" * 80)
        return 0
    else:
        print("✗ Some files are missing!")
        print("=" * 80)
        return 1


def test_python_syntax():
    """Test that all Python files have valid syntax."""

    import py_compile

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    python_files = [
        "desktop_organizer/__init__.py",
        "desktop_organizer/envs/rl_env_cfg.py",
        "desktop_organizer/envs/mimic_env_cfg.py",
        "desktop_organizer/envs/mimic_env.py",
        "desktop_organizer/mdp/rewards.py",
        "desktop_organizer/config/ppo_cfg.py",
        "scripts/train_rl.py",
        "scripts/play_rl.py",
    ]

    print("\nPYTHON SYNTAX CHECK")
    print("=" * 80)

    all_passed = True
    for file_path in python_files:
        full_path = os.path.join(base_dir, file_path)
        try:
            py_compile.compile(full_path, doraise=True)
            print(f"✓ {file_path}")
        except py_compile.PyCompileError as e:
            print(f"✗ {file_path} - SYNTAX ERROR")
            print(f"  {e}")
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("✓ All Python files have valid syntax!")
        print("=" * 80)
        return 0
    else:
        print("✗ Some files have syntax errors!")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = 0

    # Test package structure
    exit_code |= test_package_structure()

    # Test Python syntax
    exit_code |= test_python_syntax()

    if exit_code == 0:
        print("\n🎉 All smoke tests passed! Package structure is valid.")
        print("\nNext steps:")
        print("1. Install Isaac Lab: https://isaac-sim.github.io/IsaacLab/")
        print("2. Install this package: pip install -e .")
        print("3. Run training: python scripts/train_rl.py --num_envs 16 --max_iterations 10")
    else:
        print("\n❌ Some smoke tests failed. Please fix the issues above.")

    sys.exit(exit_code)
