# Training Scripts

This directory contains scripts for training and evaluating the Desktop Organizer task.

## Scripts

### RL Training & Evaluation

- `train_rl.py` - Train policy using RSL-RL (PPO)
- `play_rl.py` - Visualize trained RL policy

### BC Training & Data Generation (Coming Soon)

The following scripts can be adapted from IsaacLab's official scripts:
- Record demonstrations: Use `IsaacLab/scripts/tools/record_demos.py`
- Annotate demos: Use `IsaacLab/scripts/imitation_learning/isaaclab_mimic/annotate_demos.py`
- Generate Mimic data: Use `IsaacLab/scripts/imitation_learning/isaaclab_mimic/generate_dataset.py`
- Train BC: Use `IsaacLab/scripts/imitation_learning/robomimic/train.py`
- Replay demos: Use `IsaacLab/scripts/tools/replay_demos.py`

## Quick Start

### Train RL Policy

```bash
python scripts/train_rl.py --num_envs 4096 --max_iterations 3000 --headless
```

### Visualize Trained Policy

```bash
python scripts/play_rl.py --load_run 2026-01-23_17-58-10 --num_envs 16
```

For detailed instructions, see the main README.md.
