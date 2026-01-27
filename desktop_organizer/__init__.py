"""
Desktop Organizer: Franka robotic manipulation task for Isaac Lab

This package provides a complete pick-and-place manipulation task where a Franka robot
must grasp objects (ketchup) and place them into a basket. It supports both:
- Reinforcement Learning (RSL-RL + PPO)
- Imitation Learning (MimicGen + Robomimic BC)
"""

import gymnasium as gym

__version__ = "0.1.0"

# ========== RL Environment Registration ==========

gym.register(
    id="Isaac-Desktop-Organizer-Franka-IK-Rel-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": "desktop_organizer.envs.rl_env_cfg:FrankaDesktopOrganizerIKRelEnvCfg",
    },
    disable_env_checker=True,
)

gym.register(
    id="Isaac-Desktop-Organizer-Franka-IK-Rel-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": "desktop_organizer.envs.rl_env_cfg:FrankaDesktopOrganizerIKRelEnvCfg_PLAY",
    },
    disable_env_checker=True,
)

# ========== Mimic Environment Registration ==========

gym.register(
    id="Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0",
    entry_point="desktop_organizer.envs.mimic_env:FrankaDesktopOrganizerIKRelMimicEnv",
    kwargs={
        "env_cfg_entry_point": "desktop_organizer.envs.mimic_env_cfg:FrankaDesktopOrganizerIKRelMimicEnvCfg",
        "robomimic_bc_cfg_entry_point": "desktop_organizer/config/robomimic/bc.json",
    },
    disable_env_checker=True,
)
