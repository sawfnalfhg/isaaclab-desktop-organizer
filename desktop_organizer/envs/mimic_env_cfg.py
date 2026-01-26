"""Isaac Lab Mimic environment config for Franka Desktop Organizer IK Rel task."""

from isaaclab.envs.mimic_env_cfg import MimicEnvCfg, SubTaskConfig
from isaaclab.utils import configclass

from desktop_organizer.envs.rl_env_cfg import FrankaDesktopOrganizerIKRelEnvCfg


@configclass
class FrankaDesktopOrganizerIKRelMimicEnvCfg(FrankaDesktopOrganizerIKRelEnvCfg, MimicEnvCfg):
    """
    Isaac Lab Mimic environment config class for Franka Desktop Organizer IK Rel env.

    This configuration defines a 4-subtask manipulation task:
    1. Reach: Move end-effector to approach the ketchup object
    2. Grasp: Close gripper to grasp the ketchup
    3. Lift: Lift the ketchup to a certain height
    4. Place: Place the ketchup into the basket
    """

    def __post_init__(self):
        # post init of parents
        super().__post_init__()

        # Configure datagen settings
        self.datagen_config.name = "demo_src_desktop_organizer_isaac_lab_task_D0"
        self.datagen_config.generation_guarantee = True
        self.datagen_config.generation_keep_failed = True
        self.datagen_config.generation_num_trials = 10
        self.datagen_config.generation_select_src_per_subtask = True
        self.datagen_config.generation_transform_first_robot_pose = False
        self.datagen_config.generation_interpolate_from_last_target_pose = True
        self.datagen_config.generation_relative = True
        self.datagen_config.max_num_failures = 25
        self.datagen_config.seed = 1

        # Define subtask configurations for the desktop organizer task
        # 4 subtasks: Reach -> Grasp -> Lift -> Place
        subtask_configs = []

        # Subtask 1: Reach - Move end-effector to approach ketchup
        subtask_configs.append(
            SubTaskConfig(
                # Manipulation with respect to ketchup object frame
                object_ref="ketchup",
                # Binary indicator in "datagen_info" that signals when this subtask is finished
                subtask_term_signal="reach",
                # Time offsets for data generation when splitting trajectory into subtask segments
                subtask_term_offset_range=(3, 8),
                # Selection strategy for source subtask segment during data generation
                selection_strategy="nearest_neighbor_object",
                # Optional parameters for the selection strategy function
                selection_strategy_kwargs={"nn_k": 3},
                # Amount of action noise to apply during this subtask
                action_noise=0.03,
                # Number of interpolation steps to bridge to this subtask segment
                num_interpolation_steps=5,
                # Additional fixed steps for the robot to reach the necessary pose
                num_fixed_steps=0,
                # If True, apply action noise during the interpolation phase and execution
                apply_noise_during_interpolation=False,
                description="Reach ketchup",
                next_subtask_description="Grasp ketchup",
            )
        )

        # Subtask 2: Grasp - Close gripper to grasp ketchup
        subtask_configs.append(
            SubTaskConfig(
                object_ref="ketchup",
                subtask_term_signal="grasp",
                subtask_term_offset_range=(3, 8),
                selection_strategy="nearest_neighbor_object",
                selection_strategy_kwargs={"nn_k": 3},
                action_noise=0.03,
                num_interpolation_steps=5,
                num_fixed_steps=0,
                apply_noise_during_interpolation=False,
                description="Grasp ketchup",
                next_subtask_description="Lift ketchup",
            )
        )

        # Subtask 3: Lift - Lift ketchup to a certain height
        subtask_configs.append(
            SubTaskConfig(
                object_ref="ketchup",
                subtask_term_signal="lift",
                subtask_term_offset_range=(3, 8),
                selection_strategy="nearest_neighbor_object",
                selection_strategy_kwargs={"nn_k": 3},
                action_noise=0.03,
                num_interpolation_steps=5,
                num_fixed_steps=0,
                apply_noise_during_interpolation=False,
                description="Lift ketchup",
                next_subtask_description="Place ketchup into basket",
            )
        )

        # Subtask 4: Place - Place ketchup into basket (final subtask)
        subtask_configs.append(
            SubTaskConfig(
                # Final subtask manipulates relative to basket
                object_ref="basket",
                # End of final subtask does not need to be detected
                subtask_term_signal=None,
                # No time offsets for the final subtask
                subtask_term_offset_range=(0, 0),
                selection_strategy="nearest_neighbor_object",
                selection_strategy_kwargs={"nn_k": 3},
                action_noise=0.03,
                num_interpolation_steps=5,
                num_fixed_steps=0,
                apply_noise_during_interpolation=False,
                description="Place ketchup into basket",
            )
        )

        # Assign subtask configs to the "franka" end-effector
        self.subtask_configs["franka"] = subtask_configs
