"""Custom reward functions for Desktop Organizer task."""

from __future__ import annotations

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import Articulation, RigidObject
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import combine_frame_transforms

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def object_command_progress(
    env: ManagerBasedRLEnv,
    std: float,
    minimal_height: float,
    command_name: str,
    robot_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
) -> torch.Tensor:
    """Reward the agent for making progress from initial position to goal.

    Computes normalized progress: progress = current_distance / max_distance_at_start
    Reward = (1 - tanh(progress / std)) if object is lifted, else 0

    Args:
        env: The RL environment.
        std: Standard deviation for tanh kernel (0.4 in official config).
        minimal_height: Minimum height for the object to be considered lifted.
        command_name: Name of the command for goal position.
        robot_cfg: Robot scene entity configuration.
        object_cfg: Object scene entity configuration.

    Returns:
        Reward tensor of shape (num_envs,).
    """
    # Extract scene entities
    robot: RigidObject = env.scene[robot_cfg.name]
    object: RigidObject = env.scene[object_cfg.name]
    command = env.command_manager.get_command(command_name)

    # Get goal position in world frame
    des_pos_b = command[:, :3]
    des_pos_w, _ = combine_frame_transforms(robot.data.root_pos_w, robot.data.root_quat_w, des_pos_b)

    # Current distance from object to goal
    current_distance = torch.norm(des_pos_w - object.data.root_pos_w, dim=1)

    # Get initial object position (stored at reset)
    # For simplicity, we use the scene's initial state
    # In a real implementation, you might want to store this per-environment
    # Here we approximate max_distance as the distance at the start of episode
    # For now, we'll use a fixed max_distance estimate based on scene size
    # Basket is at ~(1.76, 1.48), objects start at ~(1.30-1.45, 1.45-1.65)
    # Max distance is roughly 0.5m
    max_distance = 1.0

    # Compute normalized progress
    progress = current_distance / max_distance

    # Only reward if object is lifted
    is_lifted = object.data.root_pos_w[:, 2] > minimal_height

    return is_lifted * (1 - torch.tanh(progress / std))


def gripper_closed_at_goal(
    env: ManagerBasedRLEnv,
    command_name: str,
    distance_threshold: float = 0.08,
    robot_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
) -> torch.Tensor:
    """Penalty for keeping gripper closed when object is at goal position.

    This function detects when the object is successfully placed at the command goal
    but the gripper has not been opened yet. Returns 1.0 for environments where
    this condition is met, 0.0 otherwise.

    Use with negative weight (e.g., -100) to penalize "holding and not releasing".

    Args:
        env: The RL environment.
        command_name: Name of the command for goal position.
        distance_threshold: Maximum distance for object to be considered at goal (meters).
        robot_cfg: Robot scene entity configuration.
        object_cfg: Object scene entity configuration.

    Returns:
        Penalty signal tensor of shape (num_envs,). 1.0 = penalty applies, 0.0 = no penalty.
    """
    # Extract scene entities
    robot: Articulation = env.scene[robot_cfg.name]
    object: RigidObject = env.scene[object_cfg.name]
    command = env.command_manager.get_command(command_name)

    # Get goal position in world frame (same as in command_progress function)
    des_pos_b = command[:, :3]
    des_pos_w, _ = combine_frame_transforms(robot.data.root_pos_w, robot.data.root_quat_w, des_pos_b)

    # Check if object is at goal position
    distance_to_goal = torch.norm(des_pos_w - object.data.root_pos_w, dim=1)
    at_goal = distance_to_goal < distance_threshold

    # Check if gripper is closed (NOT open)
    gripper_joint_ids, _ = robot.find_joints(env.cfg.gripper_joint_names)

    # Gripper is "closed" if joint position is far from the open value
    gripper_joint_1_closed = (
        torch.abs(torch.abs(robot.data.joint_pos[:, gripper_joint_ids[0]]) - env.cfg.gripper_open_val)
        > env.cfg.gripper_threshold
    )
    gripper_joint_2_closed = (
        torch.abs(torch.abs(robot.data.joint_pos[:, gripper_joint_ids[1]]) - env.cfg.gripper_open_val)
        > env.cfg.gripper_threshold
    )

    gripper_closed = torch.logical_and(gripper_joint_1_closed, gripper_joint_2_closed)

    # Penalty applies when: object at goal AND gripper closed
    penalty_signal = torch.logical_and(at_goal, gripper_closed)

    return penalty_signal.float()
