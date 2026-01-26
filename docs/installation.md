# Installation and Testing Guide

## Installation

### Step 1: Install Isaac Lab

Follow the [official Isaac Lab installation guide](https://isaac-sim.github.io/IsaacLab/source/setup/installation.html).

```bash
# Clone Isaac Lab
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Run installer
./isaaclab.sh --install
```

### Step 2: Install Desktop Organizer Package

```bash
# Clone this repository
cd /path/to/your/workspace
git clone https://github.com/<your-username>/isaaclab-desktop-organizer.git
cd isaaclab-desktop-organizer

# Install in editable mode
pip install -e .

# Optional: Install RL dependencies
pip install -e ".[rl]"
```

## Testing

### Test 1: Verify Package Installation

```bash
python -c "import desktop_organizer; print('✓ Package installed successfully')"
```

### Test 2: Verify Gym Registration

```bash
python -c "import gymnasium as gym; import desktop_organizer; \
env = gym.make('Isaac-Desktop-Organizer-Franka-IK-Rel-v0', num_envs=2); \
print('✓ Environment registered successfully')"
```

### Test 3: Run a Quick Training Test (10 iterations)

```bash
python scripts/train_rl.py \
  --num_envs 16 \
  --max_iterations 10 \
  --headless
```

Expected output:
```
[INFO] Creating environment: Isaac-Desktop-Organizer-Franka-IK-Rel-v0
[INFO] Creating PPO runner...
[INFO] Starting training for 10 iterations...
...
[INFO] Training complete!
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'omni.log'`

**Cause**: You're not running in the Isaac Sim environment.

**Solution**: Use Isaac Lab's Python environment:
```bash
cd /path/to/IsaacLab
source .venv/bin/activate  # or source _isaac_sim/setup_conda_env.sh
```

### Issue: `ModuleNotFoundError: No module named 'desktop_organizer'`

**Cause**: Package not installed or not in Python path.

**Solution**:
```bash
cd /path/to/isaaclab-desktop-organizer
pip install -e .
```

### Issue: Environment not found when calling `gym.make()`

**Cause**: `import desktop_organizer` was not called before `gym.make()`.

**Solution**: Always import the package first:
```python
import desktop_organizer  # This registers the environments
import gymnasium as gym

env = gym.make("Isaac-Desktop-Organizer-Franka-IK-Rel-v0")
```

## Next Steps

Once installation is verified, see:
- [RL Training Guide](rl_training.md)
- [Mimic + BC Guide](mimic_bc_training.md)
