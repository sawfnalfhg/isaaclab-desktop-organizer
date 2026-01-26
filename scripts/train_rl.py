"""Train Desktop Organizer task using RSL-RL (PPO).

Usage:
    python scripts/train_rl.py --num_envs 4096 --max_iterations 3000 --headless
"""

import argparse
import os
from datetime import datetime

import gymnasium as gym
from rsl_rl.runners import OnPolicyRunner

import desktop_organizer  # Register environments
from desktop_organizer.config.ppo_cfg import DesktopOrganizerPPORunnerCfg


def main():
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
        "--headless",
        action="store_true",
        help="Run in headless mode (no GUI)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda:0",
        help="Device to run on (cuda:0, cpu, etc.)",
    )
    parser.add_argument(
        "--max_iterations",
        type=str,
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
    args = parser.parse_args()

    # Create environment
    print(f"[INFO] Creating environment: {args.task}")
    env = gym.make(
        args.task,
        num_envs=args.num_envs,
        render_mode=None if args.headless else "human",
    )

    # Create runner config
    runner_cfg = DesktopOrganizerPPORunnerCfg()
    runner_cfg.algorithm.max_iterations = int(args.max_iterations)
    runner_cfg.algorithm.device = args.device

    # Create runner
    print(f"[INFO] Creating PPO runner...")
    runner = OnPolicyRunner(env, runner_cfg, log_dir=args.log_dir, device=args.device)

    # Resume or train from scratch
    if args.resume:
        if args.load_run is None:
            print("[ERROR] --load_run must be specified when using --resume")
            return
        print(f"[INFO] Resuming from: {args.load_run}")
        runner.load(args.load_run)

    # Train
    print(f"[INFO] Starting training for {args.max_iterations} iterations...")
    print(f"[INFO] Number of environments: {args.num_envs}")
    print(f"[INFO] Device: {args.device}")
    print(f"[INFO] Log directory: {args.log_dir}")
    print("=" * 80)

    runner.learn(num_learning_iterations=int(args.max_iterations), init_at_random_ep_len=True)

    # Save final model
    final_model_path = os.path.join(runner.log_dir, "model_final.pt")
    runner.save(final_model_path)
    print("=" * 80)
    print(f"[INFO] Training complete!")
    print(f"[INFO] Final model saved to: {final_model_path}")
    print(f"[INFO] Logs saved to: {runner.log_dir}")


if __name__ == "__main__":
    main()
