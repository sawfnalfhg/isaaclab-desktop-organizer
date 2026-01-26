"""Environment configurations for Desktop Organizer task."""

from .rl_env_cfg import (
    DesktopOrganizerRLEnvCfg,
    FrankaDesktopOrganizerIKRelEnvCfg,
    FrankaDesktopOrganizerIKRelEnvCfg_PLAY,
)
from .mimic_env import FrankaDesktopOrganizerIKRelMimicEnv
from .mimic_env_cfg import FrankaDesktopOrganizerIKRelMimicEnvCfg

__all__ = [
    "DesktopOrganizerRLEnvCfg",
    "FrankaDesktopOrganizerIKRelEnvCfg",
    "FrankaDesktopOrganizerIKRelEnvCfg_PLAY",
    "FrankaDesktopOrganizerIKRelMimicEnv",
    "FrankaDesktopOrganizerIKRelMimicEnvCfg",
]
