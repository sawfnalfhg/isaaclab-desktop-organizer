"""Train Desktop Organizer task using RSL-RL (PPO).

Usage:
    # 使用 IsaacLab 脚本启动（推荐）
    ./isaaclab.sh -p /path/to/train_rl.py --num_envs 4096 --max_iterations 3000 --headless

    # 或者直接运行（需要在 IsaacLab 环境中）
    python scripts/train_rl.py --num_envs 4096 --max_iterations 3000 --headless
"""

"""Launch Isaac Sim Simulator first."""

import argparse
import os

from isaaclab.app import AppLauncher

# Add argparse arguments
parser = argparse.ArgumentParser(description="Train Desktop Organizer with RSL-RL (PPO)")
parser.add_argument(
    "--task",
    type=str,
    default="Isaac-Desktop-Organizer-Franka-IK-Rel-v0",
    help="Task name (Gym environment ID)",
)
parser.add_argument(
    "--num_envs",
    type=int,
    default=4096,
    help="Number of parallel environments",
)
parser.add_argument(
    "--max_iterations",
    type=int,
    default=3000,
    help="Maximum training iterations",
)
parser.add_argument(
    "--resume",
    action="store_true",
    help="Resume from checkpoint",
)
parser.add_argument(
    "--load_run",
    type=str,
    default=None,
    help="Run folder to resume from (e.g., '2026-01-23_17-58-10')",
)
parser.add_argument(
    "--log_dir",
    type=str,
    default="./logs/rsl_rl/desktop_organizer",
    help="Directory to save logs and checkpoints",
)

# Append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)

# Parse the arguments
args_cli = parser.parse_args()

# Launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import gymnasium as gym
import torch
from rsl_rl.runners import OnPolicyRunner

import desktop_organizer  # Register environments
from desktop_organizer.config.ppo_cfg import DesktopOrganizerPPORunnerCfg
from isaaclab_tasks.utils import parse_env_cfg
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper


def main():
    """Train the RL agent."""

    # Parse environment configuration
    print(f"[INFO] Parsing environment config for: {args_cli.task}")
    env_cfg = parse_env_cfg(
        task_name=args_cli.task,
        device=args_cli.device,
        num_envs=args_cli.num_envs,
    )

    # Create environment
    print(f"[INFO] Creating environment: {args_cli.task}")
    env = gym.make(args_cli.task, cfg=env_cfg)

    # Wrap environment for RSL-RL
    print(f"[INFO] Wrapping environment with RslRlVecEnvWrapper...")
    env = RslRlVecEnvWrapper(env)

    # Create runner config
    runner_cfg = DesktopOrganizerPPORunnerCfg()
    runner_cfg.max_iterations = args_cli.max_iterations

    # Create runner
    print(f"[INFO] Creating PPO runner...")
    runner = OnPolicyRunner(env, runner_cfg.to_dict(), log_dir=args_cli.log_dir, device=args_cli.device)

    # Resume or train from scratch
    if args_cli.resume:
        if args_cli.load_run is None:
            print("[ERROR] --load_run must be specified when using --resume")
            simulation_app.close()
            return
        print(f"[INFO] Resuming from: {args_cli.load_run}")
        runner.load(args_cli.load_run)

    # Train
    print(f"[INFO] Starting training for {args_cli.max_iterations} iterations...")
    print(f"[INFO] Number of environments: {args_cli.num_envs}")
    print(f"[INFO] Device: {args_cli.device}")
    print(f"[INFO] Log directory: {args_cli.log_dir}")
    print("=" * 80)

    runner.learn(num_learning_iterations=args_cli.max_iterations, init_at_random_ep_len=True)

    # Save final model
    final_model_path = os.path.join(runner.log_dir, "model_final.pt")
    runner.save(final_model_path)
    print("=" * 80)
    print(f"[INFO] Training complete!")
    print(f"[INFO] Final model saved to: {final_model_path}")
    print(f"[INFO] Logs saved to: {runner.log_dir}")

    # Close the simulator
    env.close()
    simulation_app.close()


if __name__ == "__main__":
    # Run the main function
    main()
    # Simulation app is already closed in main()
