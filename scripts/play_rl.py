"""Visualize trained Desktop Organizer RL policy.

Usage:
    # 使用 IsaacLab 脚本启动（推荐）
    ./isaaclab.sh -p /path/to/play_rl.py --load_run 2026-01-23_17-58-10 --num_envs 16

    # 或者直接运行（需要在 IsaacLab 环境中）
    python scripts/play_rl.py --load_run 2026-01-23_17-58-10 --num_envs 16
"""

"""Launch Isaac Sim Simulator first."""

import argparse
import os
import torch

from isaaclab.app import AppLauncher

# Add argparse arguments
parser = argparse.ArgumentParser(description="Visualize Desktop Organizer RL policy")
parser.add_argument(
    "--task",
    type=str,
    default="Isaac-Desktop-Organizer-Franka-IK-Rel-Play-v0",
    help="Task name for evaluation (usually with -Play suffix)",
)
parser.add_argument(
    "--num_envs",
    type=int,
    default=16,
    help="Number of parallel environments for visualization",
)
parser.add_argument(
    "--load_run",
    type=str,
    required=True,
    help="Run folder to load model from (e.g., '2026-01-23_17-58-10')",
)
parser.add_argument(
    "--checkpoint",
    type=str,
    default="model_final.pt",
    help="Checkpoint filename (default: model_final.pt)",
)
parser.add_argument(
    "--device",
    type=str,
    default="cuda:0",
    help="Device to run on",
)
parser.add_argument(
    "--log_dir",
    type=str,
    default="./logs/rsl_rl/desktop_organizer",
    help="Directory where logs are stored",
)

# Append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)

# Parse the arguments
args_cli = parser.parse_args()

# Launch omniverse app (with rendering enabled for visualization)
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import gymnasium as gym
from rsl_rl.runners import OnPolicyRunner

import desktop_organizer  # Register environments
from desktop_organizer.config.ppo_cfg import DesktopOrganizerPPORunnerCfg


def main():
    """Run the trained policy for visualization."""

    # Create environment (in non-headless mode for visualization)
    print(f"[INFO] Creating environment: {args_cli.task}")
    env = gym.make(
        args_cli.task,
        num_envs=args_cli.num_envs,
    )

    # Create runner config
    runner_cfg = DesktopOrganizerPPORunnerCfg()

    # Create runner
    print(f"[INFO] Creating PPO runner...")
    runner = OnPolicyRunner(env, runner_cfg, log_dir=args_cli.log_dir, device=args_cli.device)

    # Load checkpoint
    checkpoint_path = os.path.join(args_cli.log_dir, args_cli.load_run, args_cli.checkpoint)
    if not os.path.exists(checkpoint_path):
        print(f"[ERROR] Checkpoint not found: {checkpoint_path}")
        env.close()
        simulation_app.close()
        return

    print(f"[INFO] Loading checkpoint: {checkpoint_path}")
    runner.load(checkpoint_path)

    # Run policy
    print(f"[INFO] Running policy for visualization...")
    print(f"[INFO] Number of environments: {args_cli.num_envs}")
    print(f"[INFO] Device: {args_cli.device}")
    print("=" * 80)
    print("[INFO] Press Ctrl+C to stop")

    # Inference loop
    obs, _ = env.reset()
    try:
        with torch.no_grad():
            while simulation_app.is_running():
                actions = runner.get_inference_policy(device=args_cli.device)(obs)
                obs, rewards, dones, truncated, info = env.step(actions)

                # Print success rate periodically
                if "episode" in info:
                    success_rate = info["episode"].get("success_rate", 0.0)
                    if success_rate > 0:
                        print(f"Success rate: {success_rate:.2%}")
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")

    # Close
    env.close()
    simulation_app.close()


if __name__ == "__main__":
    # Run the main function
    main()
    # Simulation app is already closed in main()
