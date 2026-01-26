"""Configuration for the desktop organizer RL task."""

from dataclasses import MISSING
from pathlib import Path

import torch

import isaaclab.sim as sim_utils
import isaaclab.envs.mdp as isaaclab_mdp
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors.frame_transformer.frame_transformer_cfg import FrameTransformerCfg, OffsetCfg
from isaaclab.sim.spawners.from_files.from_files_cfg import GroundPlaneCfg, UsdFileCfg
from isaaclab.utils import configclass
from isaaclab.controllers.differential_ik_cfg import DifferentialIKControllerCfg
from isaaclab.envs.mdp.actions.actions_cfg import DifferentialInverseKinematicsActionCfg

# Import custom MDP functions
from desktop_organizer import mdp

# Import official MDP functions
from isaaclab_tasks.manager_based.manipulation.place import mdp as place_mdp
from isaaclab_tasks.manager_based.manipulation.stack import mdp as stack_mdp
from isaaclab_tasks.manager_based.manipulation.stack.mdp import franka_stack_events

# Import Franka robot configuration
from isaaclab_assets.robots.franka import FRANKA_PANDA_HIGH_PD_CFG

# Get the absolute path to the USD scene file
PKG_DIR = Path(__file__).resolve().parent.parent.parent
USD_SCENE_PATH = PKG_DIR / "assets" / "scenes" / "Collected_table_clean" / "table_clean.usd"


##
# Scene definition
##
@configclass
class DesktopOrganizerRLSceneCfg(InteractiveSceneCfg):
    """Configuration for the desktop organizer RL scene."""

    # Load assembled scene USD
    scene_usd = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Scene",
        spawn=UsdFileCfg(usd_path=str(USD_SCENE_PATH)),
    )

    # Robot
    robot = FRANKA_PANDA_HIGH_PD_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot",
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(1.53773, 1.88609, 0.42492),
            rot=(0.70710678, 0.0, 0.0, -0.70710678),
            joint_pos={
                "panda_joint1": 0.0,
                "panda_joint2": -0.79,
                "panda_joint3": 0.0,
                "panda_joint4": -2.356,
                "panda_joint5": 0.0,
                "panda_joint6": 1.57,
                "panda_joint7": 0.785,
                "panda_finger_joint1": 0.04,
                "panda_finger_joint2": 0.04,
            },
        ),
    )

    # End-effector frame
    ee_frame: FrameTransformerCfg = FrameTransformerCfg(
        prim_path="{ENV_REGEX_NS}/Robot/panda_link0",
        debug_vis=False,
        target_frames=[
            FrameTransformerCfg.FrameCfg(
                prim_path="{ENV_REGEX_NS}/Robot/panda_hand",
                name="end_effector",
                offset=OffsetCfg(pos=[0.0, 0.0, 0.1034]),
            )
        ],
    )

    # Objects
    orange_juice = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Scene/orange_juice",
        spawn=None,
        init_state=RigidObjectCfg.InitialStateCfg(
            pos=(1.39764, 1.38226, 0.52),
            rot=(0.70710678, 0.70710678, 0.0, 0.0),
        ),
    )
    ketchup = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Scene/ketchup",
        spawn=None,
        init_state=RigidObjectCfg.InitialStateCfg(
            pos=(1.38508, 1.60167, 0.50771),
            rot=(0.70710678, 0.70710678, 0.0, 0.0),
        ),
    )
    cream_cheese = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Scene/cream_cheese",
        spawn=None,
        init_state=RigidObjectCfg.InitialStateCfg(
            pos=(1.1565, 1.46713, 0.45974),
            rot=(0.70710678, 0.70710678, 0.0, 0.0),
        ),
    )

    basket = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Scene/basket",
        spawn=None,
        init_state=RigidObjectCfg.InitialStateCfg(
            pos=(1.77, 1.48, 0.48),
            rot=(1.0, 0.0, 0.0, 0.0),
        ),
    )

    table = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Scene/living_room_table",
        spawn=None,
    )

    # Ground plane
    ground = AssetBaseCfg(
        prim_path="/World/GroundPlane",
        spawn=GroundPlaneCfg(),
    )

    # Lighting
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=3000.0),
    )


##
# MDP settings
##
@configclass
class CommandsCfg:
    """Command specifications for the MDP."""

    # Target position: above basket (robot local coordinates, fixed)
    object_pose = isaaclab_mdp.UniformPoseCommandCfg(
        asset_name="robot",
        body_name="panda_hand",
        resampling_time_range=(5.0, 5.0),
        debug_vis=True,
        ranges=isaaclab_mdp.UniformPoseCommandCfg.Ranges(
            # Basket fixed position (1.76, 1.48) in robot local coordinates
            pos_x=(0.406, 0.406),  # Fixed X (world coord 1.76)
            pos_y=(0.222, 0.222),  # Fixed Y (world coord 1.48)
            pos_z=(0.375, 0.375),  # Fixed Z (world coord 0.8)
            roll=(0.0, 0.0),
            pitch=(0.0, 0.0),
            yaw=(0.0, 0.0)
        ),
    )


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""

    # Will be set by agent env cfg
    arm_action: isaaclab_mdp.JointPositionActionCfg | isaaclab_mdp.DifferentialInverseKinematicsActionCfg = MISSING
    gripper_action: isaaclab_mdp.BinaryJointPositionActionCfg = MISSING


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for policy group."""

        # Robot state
        joint_pos = ObsTerm(func=isaaclab_mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=isaaclab_mdp.joint_vel_rel)

        # Ketchup position (in robot root frame)
        object_position = ObsTerm(func=isaaclab_mdp.object_position_in_robot_root_frame, params={"object_cfg": SceneEntityCfg("ketchup")})

        # Target position (basket center above)
        target_object_position = ObsTerm(func=isaaclab_mdp.generated_commands, params={"command_name": "object_pose"})

        # Previous actions
        actions = ObsTerm(func=isaaclab_mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()


@configclass
class RewardsCfg:
    """Reward terms for the MDP (aligned with official Lift task + command_progress)."""

    # 1. Reaching: end-effector approaching ketchup
    reaching_object = RewTerm(
        func=isaaclab_mdp.object_ee_distance,
        params={"std": 0.1, "object_cfg": SceneEntityCfg("ketchup")},
        weight=5.0,
    )

    # 2. Lifting: ketchup being lifted (reduced to avoid "holding and not releasing")
    lifting_object = RewTerm(
        func=isaaclab_mdp.object_is_lifted,
        params={"minimal_height": 0.52, "object_cfg": SceneEntityCfg("ketchup")},
        weight=10.0,
    )

    # 3. Command progress: overall progress from initial to goal (reduced weight)
    command_progress = RewTerm(
        func=mdp.object_command_progress,
        params={
            "std": 0.8,
            "minimal_height": 0.52,
            "command_name": "object_pose",
            "object_cfg": SceneEntityCfg("ketchup"),
        },
        weight=30.0,
    )

    # 4. Object goal tracking (coarse)
    object_goal_tracking = RewTerm(
        func=isaaclab_mdp.object_goal_distance,
        params={"std": 0.3, "minimal_height": 0.52, "command_name": "object_pose", "object_cfg": SceneEntityCfg("ketchup")},
        weight=10.0,
    )

    # 5. Object goal tracking fine-grained (KEY reduction!)
    object_goal_tracking_fine_grained = RewTerm(
        func=isaaclab_mdp.object_goal_distance,
        params={"std": 0.05, "minimal_height": 0.52, "command_name": "object_pose", "object_cfg": SceneEntityCfg("ketchup")},
        weight=50.0,
    )

    # 6. Success reward: ketchup successfully placed in basket (VERY HIGH reward)
    success_reward = RewTerm(
        func=place_mdp.object_a_is_into_b,
        params={
            "robot_cfg": SceneEntityCfg("robot"),
            "object_a_cfg": SceneEntityCfg("ketchup"),
            "object_b_cfg": SceneEntityCfg("basket"),
            "xy_threshold": 0.11,
            "height_threshold": 0.20,
            "height_diff": 0.0,
        },
        weight=20000.0,
    )

    # 7. Gripper closed at goal penalty: penalize when object is at goal but gripper not opened
    gripper_closed_penalty = RewTerm(
        func=mdp.gripper_closed_at_goal,
        params={
            "command_name": "object_pose",
            "distance_threshold": 0.08,
            "robot_cfg": SceneEntityCfg("robot"),
            "object_cfg": SceneEntityCfg("ketchup"),
        },
        weight=-100.0,
    )

    # Action penalties
    action_rate = RewTerm(func=isaaclab_mdp.action_rate_l2, weight=-1e-4)

    joint_vel = RewTerm(
        func=isaaclab_mdp.joint_vel_l2,
        weight=-1e-4,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    time_out = DoneTerm(func=isaaclab_mdp.time_out, time_out=True)

    # Ketchup dropping (failure)
    object_dropping = DoneTerm(
        func=isaaclab_mdp.root_height_below_minimum,
        params={"minimum_height": 0.3, "asset_cfg": SceneEntityCfg("ketchup")},
    )

    # Success: ketchup successfully placed in basket
    success = DoneTerm(
        func=place_mdp.object_a_is_into_b,
        params={
            "robot_cfg": SceneEntityCfg("robot"),
            "object_a_cfg": SceneEntityCfg("ketchup"),
            "object_b_cfg": SceneEntityCfg("basket"),
            "xy_threshold": 0.11,
            "height_threshold": 0.20,
            "height_diff": 0.0,
        },
    )


@configclass
class CurriculumCfg:
    """Curriculum terms for the MDP (gradually increase penalty weights)."""

    action_rate = CurrTerm(
        func=isaaclab_mdp.modify_reward_weight,
        params={"term_name": "action_rate", "weight": -1e-1, "num_steps": 10000},
    )

    joint_vel = CurrTerm(
        func=isaaclab_mdp.modify_reward_weight,
        params={"term_name": "joint_vel", "weight": -1e-1, "num_steps": 10000},
    )


@configclass
class EventCfg:
    """Configuration for environment reset events."""

    reset_scene = EventTerm(
        func=isaaclab_mdp.reset_scene_to_default,
        mode="reset",
        params={"reset_joint_targets": True},
    )

    # Randomize object positions
    randomize_ketchup = EventTerm(
        func=franka_stack_events.randomize_object_pose,
        mode="reset",
        params={
            "pose_range": {
                "x": (1.25, 1.50),  # Medium generalization: 25cm range
                "y": (1.40, 1.65),  # Medium generalization: 25cm range
                "z": (0.50771, 0.50771),
                "roll": (1.5708, 1.5708),
                "pitch": (0.0, 0.0),
                "yaw": (-0.3, 0.3),
            },
            "min_separation": 0.0,
            "asset_cfgs": [SceneEntityCfg("ketchup")],
        },
    )

    randomize_orange_juice = EventTerm(
        func=franka_stack_events.randomize_object_pose,
        mode="reset",
        params={
            "pose_range": {
                "x": (1.10, 1.60),  # Medium generalization: 50cm range
                "y": (1.20, 1.80),  # Medium generalization: 60cm range
                "z": (0.52, 0.52),
                "roll": (1.5708, 1.5708),
                "pitch": (0.0, 0.0),
                "yaw": (-0.5, 0.5),
            },
            "min_separation": 0.0,
            "asset_cfgs": [SceneEntityCfg("orange_juice")],
        },
    )

    randomize_cream_cheese = EventTerm(
        func=franka_stack_events.randomize_object_pose,
        mode="reset",
        params={
            "pose_range": {
                "x": (1.10, 1.60),
                "y": (1.20, 1.80),
                "z": (0.45974, 0.45974),
                "roll": (1.5708, 1.5708),
                "pitch": (0.0, 0.0),
                "yaw": (-0.5, 0.5),
            },
            "min_separation": 0.0,
            "asset_cfgs": [SceneEntityCfg("cream_cheese")],
        },
    )

    randomize_basket = EventTerm(
        func=franka_stack_events.randomize_object_pose,
        mode="reset",
        params={
            "pose_range": {
                "x": (1.76, 1.76),  # Fixed X
                "y": (1.48, 1.48),  # Fixed Y
                "z": (0.48, 0.48),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
            "min_separation": 0.0,
            "asset_cfgs": [SceneEntityCfg("basket")],
        },
    )


##
# Base Environment Configuration
##
@configclass
class DesktopOrganizerRLEnvCfg(ManagerBasedRLEnvCfg):
    """Configuration for the desktop organizer RL environment."""

    # Scene settings
    scene: DesktopOrganizerRLSceneCfg = DesktopOrganizerRLSceneCfg(num_envs=4096, env_spacing=2.5)
    # Basic settings
    commands: CommandsCfg = CommandsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        """Post initialization."""
        # general settings
        self.decimation = 2
        self.episode_length_s = 5.0
        # simulation settings
        self.sim.dt = 0.01  # 100Hz
        self.sim.render_interval = self.decimation

        # Gripper configuration (for object_a_is_into_b success check)
        self.gripper_joint_names = ["panda_finger_joint1", "panda_finger_joint2"]
        self.gripper_open_val = 0.04
        self.gripper_threshold = 0.01


##
# Franka with IK Control Configuration
##
@configclass
class FrankaDesktopOrganizerIKRelEnvCfg(DesktopOrganizerRLEnvCfg):
    """Configuration for Franka desktop organizer RL with IK relative control."""

    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # Set actions for IK control
        self.actions.arm_action = isaaclab_mdp.DifferentialInverseKinematicsActionCfg(
            asset_name="robot",
            joint_names=["panda_joint.*"],
            body_name="panda_hand",
            controller=DifferentialIKControllerCfg(command_type="pose", use_relative_mode=True, ik_method="dls"),
            scale=0.5,
            body_offset=DifferentialInverseKinematicsActionCfg.OffsetCfg(pos=[0.0, 0.0, 0.107]),
        )

        self.actions.gripper_action = isaaclab_mdp.BinaryJointPositionActionCfg(
            asset_name="robot",
            joint_names=["panda_finger.*"],
            open_command_expr={"panda_finger_.*": 0.04},
            close_command_expr={"panda_finger_.*": 0.0},
        )


@configclass
class FrankaDesktopOrganizerIKRelEnvCfg_PLAY(FrankaDesktopOrganizerIKRelEnvCfg):
    """Configuration for playing (evaluation) mode."""

    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # make a smaller scene for play
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # disable randomization for play
        self.observations.policy.enable_corruption = False
