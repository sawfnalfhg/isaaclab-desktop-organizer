# 🚀 IsaacLab 独立包使用指南

## 📍 问题 1：独立包应该放在哪里？

### 推荐目录结构

```bash
/home/your-username/
├── IsaacLab/                        # Isaac Lab 主仓库（已有）
│   ├── isaaclab.sh
│   ├── scripts/
│   └── source/
│
└── workspace/                       # 你的工作目录（推荐新建）
    └── isaaclab-desktop-organizer/  # 独立包（当前在 /root/ 下）
        ├── README.md
        ├── desktop_organizer/
        └── scripts/
```

### 移动独立包到推荐位置（可选）

```bash
# 创建工作目录
mkdir -p ~/workspace

# 移动独立包
mv /root/isaaclab-desktop-organizer ~/workspace/

# 新位置
cd ~/workspace/isaaclab-desktop-organizer
```

---

## 🔧 问题 2：使用 isaaclab.sh 启动脚本

### ✅ 完整操作步骤

#### Step 1: 安装独立包到 IsaacLab 环境

```bash
# 进入 IsaacLab 目录
cd /root/IsaacLab

# 激活 IsaacLab 虚拟环境
source _isaac_sim/setup_conda_env.sh
# 或者 source .venv/bin/activate

# 安装独立包（使用绝对路径）
pip install -e /root/isaaclab-desktop-organizer

# 验证安装成功
python -c "import desktop_organizer; print('✓ 安装成功')"
```

**重要**：`-e` 表示 editable 模式，你修改代码后不需要重新安装。

---

#### Step 2: 使用 isaaclab.sh 启动训练

**方案 A：使用绝对路径（最简单）**

```bash
# 进入 IsaacLab 目录
cd /root/IsaacLab

# 使用 isaaclab.sh 启动训练（用绝对路径）
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless

# 可视化训练好的策略
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/play_rl.py \
  --load_run 2026-01-23_17-58-10 \
  --num_envs 16
```

**方案 B：创建软链接（推荐给经常使用的用户）**

```bash
# 进入 IsaacLab/scripts 目录
cd /root/IsaacLab/scripts

# 创建软链接
ln -s /root/isaaclab-desktop-organizer/scripts/train_rl.py \
      desktop_organizer_train.py

ln -s /root/isaaclab-desktop-organizer/scripts/play_rl.py \
      desktop_organizer_play.py

# 使用相对路径启动（更简洁）
cd /root/IsaacLab
./isaaclab.sh -p scripts/desktop_organizer_train.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless
```

---

## 📝 完整训练命令示例

### 1️⃣ 从头训练（推荐参数）

```bash
cd /root/IsaacLab

./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless \
  --device cuda:0
```

**参数说明**：
- `--num_envs 4096` - 并行环境数（越多越快，需要足够的 GPU 内存）
- `--max_iterations 3000` - 训练轮数（2500-3000 可达到 85% 成功率）
- `--headless` - 无 GUI 模式（加速训练）
- `--device cuda:0` - 使用第一张 GPU

---

### 2️⃣ 继续训练

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 5000 \
  --resume \
  --load_run 2026-01-23_17-58-10 \
  --headless
```

**参数说明**：
- `--resume` - 从检查点继续训练
- `--load_run 2026-01-23_17-58-10` - 指定要恢复的训练 run（从 logs 目录查找）

---

### 3️⃣ 可视化训练好的策略

```bash
# 不加 --headless，会显示 GUI
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/play_rl.py \
  --load_run 2026-01-23_17-58-10 \
  --num_envs 16 \
  --device cuda:0
```

**参数说明**：
- `--num_envs 16` - 可视化时用少量环境（太多会卡顿）
- 不加 `--headless`，会自动打开 Isaac Sim GUI

---

## 🔍 查找训练日志和模型

### 日志位置

```bash
cd /root/IsaacLab

# 查看所有训练 run
ls -lht logs/rsl_rl/desktop_organizer/

# 输出示例
# drwxr-xr-x 2026-01-23_17-58-10/
# drwxr-xr-x 2026-01-22_14-32-45/
# ...
```

### 模型文件

```bash
# 每个 run 目录下有：
logs/rsl_rl/desktop_organizer/2026-01-23_17-58-10/
├── model_final.pt            # 最终模型
├── model_500.pt              # 第 500 轮检查点
├── model_1000.pt             # 第 1000 轮检查点
└── summaries/                # TensorBoard 日志
```

### 查看训练曲线（TensorBoard）

```bash
cd /root/IsaacLab

# 激活虚拟环境
source _isaac_sim/setup_conda_env.sh

# 启动 TensorBoard
tensorboard --logdir=logs/rsl_rl/desktop_organizer --port=6006

# 打开浏览器访问 http://localhost:6006
```

---

## ⚙️ 自定义配置

### 修改环境参数

编辑 `desktop_organizer/envs/rl_env_cfg.py`:

```python
# 修改并行环境数（默认 4096）
scene: DesktopOrganizerRLSceneCfg = DesktopOrganizerRLSceneCfg(
    num_envs=2048,  # 改成 2048
    env_spacing=2.5
)

# 修改 episode 长度（默认 5 秒）
self.episode_length_s = 8.0  # 改成 8 秒

# 修改物体随机范围
randomize_ketchup = EventTerm(
    params={
        "pose_range": {
            "x": (1.20, 1.55),  # 扩大范围
            "y": (1.35, 1.70),
            ...
        },
    },
)
```

### 修改奖励权重

编辑 `desktop_organizer/envs/rl_env_cfg.py`:

```python
@configclass
class RewardsCfg:
    reaching_object = RewTerm(weight=10.0, ...)  # 从 5.0 改成 10.0
    success_reward = RewTerm(weight=30000.0, ...)  # 从 20000.0 改成 30000.0
```

### 修改 PPO 超参数

编辑 `desktop_organizer/config/ppo_cfg.py`:

```python
@configclass
class DesktopOrganizerPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 32  # 从 24 改成 32
    policy = RslRlPpoActorCriticCfg(
        actor_hidden_dims=[512, 256, 128],  # 增大网络
        ...
    )
    algorithm = RslRlPpoAlgorithmCfg(
        learning_rate=1e-3,  # 从 3e-4 改成 1e-3
        ...
    )
```

**修改后无需重新安装**，直接重新训练即可生效。

---

## 🐛 常见问题排查

### 问题 1：ImportError: No module named 'desktop_organizer'

**原因**：没有安装独立包

**解决**：
```bash
cd /root/IsaacLab
source _isaac_sim/setup_conda_env.sh
pip install -e /root/isaaclab-desktop-organizer
```

---

### 问题 2：Environment not registered

**原因**：环境 ID 不存在

**解决**：
```bash
# 检查已注册的环境
python -c "import gymnasium as gym; import desktop_organizer; print(list(gym.envs.registry.keys()))" | grep Desktop

# 应该输出：
# Isaac-Desktop-Organizer-Franka-IK-Rel-v0
# Isaac-Desktop-Organizer-Franka-IK-Rel-Play-v0
# Isaac-Desktop-Organizer-Franka-Mimic-IK-Rel-v0
```

---

### 问题 3：CUDA out of memory

**原因**：并行环境数太多

**解决**：
```bash
# 减少并行环境数
./isaaclab.sh -p ... --num_envs 2048  # 从 4096 改成 2048
```

---

### 问题 4：USD 文件找不到

**原因**：USD 路径错误

**解决**：
```bash
# 检查 USD 文件是否存在
ls -lh /root/isaaclab-desktop-organizer/assets/scenes/Collected_table_clean/table_clean.usd

# 应该看到文件（29KB）
```

---

## 📊 性能优化建议

### GPU 内存优化

| 并行环境数 | GPU 内存需求 | 训练速度 | 推荐场景 |
|-----------|-------------|---------|---------|
| 1024 | ~8GB | 慢 | 小显存 GPU |
| 2048 | ~16GB | 中等 | RTX 3090 |
| 4096 | ~24GB | 快 | RTX 4090 |
| 8192 | ~40GB | 很快 | A100 |

### 训练速度优化

```bash
# 使用 headless 模式（必需）
--headless

# 减少 episode 长度（可选，会影响性能）
# 在 rl_env_cfg.py 中修改：
self.episode_length_s = 3.0  # 从 5.0 改成 3.0

# 使用混合精度训练（高级）
--enable_amp
```

---

## 🎯 完整工作流程示例

```bash
# ==================== 设置阶段 ====================
# 1. 进入 IsaacLab
cd /root/IsaacLab

# 2. 激活环境
source _isaac_sim/setup_conda_env.sh

# 3. 安装独立包
pip install -e /root/isaaclab-desktop-organizer

# ==================== 训练阶段 ====================
# 4. 开始训练
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless

# ==================== 监控阶段 ====================
# 5. 另开一个终端，查看训练曲线
tensorboard --logdir=logs/rsl_rl/desktop_organizer --port=6006
# 打开浏览器访问 http://localhost:6006

# ==================== 测试阶段 ====================
# 6. 训练完成后，找到最新的 run
ls -lt logs/rsl_rl/desktop_organizer/ | head -5

# 7. 可视化策略
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/play_rl.py \
  --load_run 2026-01-23_17-58-10 \
  --num_envs 16
```

---

**🎉 现在你可以使用 isaaclab.sh 脚本启动你的独立包了！**
