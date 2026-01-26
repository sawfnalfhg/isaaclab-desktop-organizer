"""Visualize trained Desktop Organizer RL policy.

Usage:
    python scripts/play_rl.py --load_run 2026-01-23_17-58-10 --num_envs 16
"""

import argparse
import os
import torch

import gymnasium as gym
from rsl_rl.runners import OnPolicyRunner

import desktop_organizer  # Register environments
from desktop_organizer.config.ppo_cfg import DesktopOrganizerPPORunnerCfg


def main():
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
    args = parser.parse_args()

    # Create environment (in non-headless mode for visualization)
    print(f"[INFO] Creating environment: {args.task}")
    env = gym.make(
        args.task,
        num_envs=args.num_envs,
        render_mode="human",  # Enable visualization
    )

    # Create runner config
    runner_cfg = DesktopOrganizerPPORunnerCfg()

    # Create runner
    print(f"[INFO] Creating PPO runner...")
    runner = OnPolicyRunner(env, runner_cfg, log_dir=args.log_dir, device=args.device)

    # Load checkpoint
    checkpoint_path = os.path.join(args.log_dir, args.load_run, args.checkpoint)
    if not os.path.exists(checkpoint_path):
        print(f"[ERROR] Checkpoint not found: {checkpoint_path}")
        return

    print(f"[INFO] Loading checkpoint: {checkpoint_path}")
    runner.load(checkpoint_path)

    # Run policy
    print(f"[INFO] Running policy for visualization...")
    print(f"[INFO] Number of environments: {args.num_envs}")
    print(f"[INFO] Device: {args.device}")
    print("=" * 80)
    print("[INFO] Press Ctrl+C to stop")

    # Inference loop
    obs, _ = env.reset()
    with torch.no_grad():
        while True:
            actions = runner.get_inference_policy(device=args.device)(obs)
            obs, rewards, dones, truncated, info = env.step(actions)

            # Print success rate
            if "episode" in info:
                success_rate = info["episode"].get("success_rate", 0.0)
                print(f"Success rate: {success_rate:.2%}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")
