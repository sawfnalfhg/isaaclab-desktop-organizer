# train_rl.py 模型覆盖问题修复说明

> ⚠️ **文档状态：已过时**
>
> 此文档记录的问题已通过替换为官方完整版 train.py 解决（2026-01-27）。
>
> **当前状态**：`/root/isaaclab-desktop-organizer/scripts/train_rl.py` 现在是 IsaacLab 官方 `train.py` 的完整副本（207 行），包含所有功能（Hydra 配置、种子设置、配置导出、Git 追踪、视频录制、多 GPU 支持等），唯一修改是添加了 `import desktop_organizer  # noqa: F401` 这一行。
>
> **详细说明**：请查看 [SCRIPTS_ALIGNMENT_COMPLETE.md](SCRIPTS_ALIGNMENT_COMPLETE.md)

---

## 🐛 发现的问题

**问题描述**：外部包的 `train_rl.py` 每次训练都会覆盖同一个目录，导致之前的训练模型丢失。

### 原始实现（错误）❌

```python
# 第 52 行：使用固定的 log_dir
parser.add_argument(
    "--log_dir",
    type=str,
    default="./logs/rsl_rl/desktop_organizer",  # ❌ 固定路径
    help="Directory to save logs and checkpoints",
)

# 第 103 行：直接使用固定路径
runner = OnPolicyRunner(env, runner_cfg.to_dict(), log_dir=args_cli.log_dir, device=args_cli.device)
```

**结果**：每次训练都写入同一个目录
```
logs/rsl_rl/desktop_organizer/
├── model_*.pt              ❌ 每次都被覆盖
├── model_final.pt          ❌ 每次都被覆盖
└── summaries/              ❌ 每次都被覆盖
```

---

## ✅ 修复后的实现

### 关键修改

1. **添加 datetime 导入**
```python
from datetime import datetime
```

2. **动态生成时间戳文件夹**
```python
# Specify directory for logging experiments (root path)
log_root_path = os.path.abspath(args_cli.log_dir)
print(f"[INFO] Logging experiment in directory: {log_root_path}")

# Create unique log directory for this run: {timestamp}
log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # ✅ 动态时间戳
log_dir = os.path.join(log_root_path, log_dir)
```

3. **修复 resume 逻辑**
```python
# Save resume path before creating new log_dir
resume_path = None
if args_cli.resume:
    if args_cli.load_run is None:
        print("[ERROR] --load_run must be specified when using --resume")
        simulation_app.close()
        return
    resume_path = os.path.join(log_root_path, args_cli.load_run)  # ✅ 正确拼接路径
    print(f"[INFO] Resuming from: {resume_path}")

# Create runner
runner = OnPolicyRunner(env, runner_cfg.to_dict(), log_dir=log_dir, device=args_cli.device)

# Load checkpoint if resuming
if args_cli.resume:
    print(f"[INFO] Loading model checkpoint from: {resume_path}")
    runner.load(resume_path)  # ✅ 使用完整路径
```

### 修复后的目录结构

```
logs/rsl_rl/desktop_organizer/
├── 2026-01-23_17-58-10/    ✅ 第一次训练（3000 轮）
│   ├── model_*.pt
│   ├── model_final.pt
│   └── summaries/
├── 2026-01-24_10-30-22/    ✅ 第二次训练（5000 轮）
│   ├── model_*.pt
│   ├── model_final.pt
│   └── summaries/
└── 2026-01-25_14-15-33/    ✅ 第三次训练（从第二次继续）
    ├── model_*.pt
    ├── model_final.pt
    └── summaries/
```

---

## 📖 使用说明

### 1. `--load_run` 参数详解

`--load_run` 是一个**时间戳格式的文件夹名称**，用于指定要恢复的训练运行。

**格式**：`YYYY-MM-DD_HH-MM-SS`（年-月-日_时-分-秒）

**示例**：
- `2026-01-23_17-58-10`
- `2026-01-24_10-30-22`
- `2026-01-25_14-15-33`

**位置**：
```
./logs/rsl_rl/desktop_organizer/{--load_run}/
                                 ↑
                          这就是 --load_run 参数
```

---

### 2. 从头开始训练（新模型）

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --headless
```

**结果**：
- 自动创建新的时间戳文件夹，如 `2026-01-27_19-30-15/`
- 模型保存到 `./logs/rsl_rl/desktop_organizer/2026-01-27_19-30-15/`

---

### 3. 继续训练（Resume）

#### Step 1: 找到要继续的训练运行

```bash
# 列出所有训练运行
ls -la ./logs/rsl_rl/desktop_organizer/

# 输出示例:
# drwxr-xr-x  2026-01-23_17-58-10    ← 第一次训练（3000 轮）
# drwxr-xr-x  2026-01-24_10-30-22    ← 第二次训练（5000 轮）
```

#### Step 2: 使用 `--resume` 和 `--load_run` 继续训练

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 5000 \
  --resume \
  --load_run 2026-01-24_10-30-22 \
  --headless
```

**重要说明**：
- ✅ `--resume` 和 `--load_run` **必须同时使用**
- ✅ 会创建**新的时间戳文件夹**（如 `2026-01-27_19-35-20/`）
- ✅ 从指定的检查点（`2026-01-24_10-30-22/`）加载模型
- ✅ **不会覆盖原始训练运行**

**文件夹结构**：
```
logs/rsl_rl/desktop_organizer/
├── 2026-01-24_10-30-22/    ← 原始训练（5000 轮）[不会被修改]
└── 2026-01-27_19-35-20/    ← 继续训练（从 5000 轮 → 8000 轮）[新建]
```

---

### 4. 评估训练好的模型

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/play_rl.py \
  --load_run 2026-01-24_10-30-22 \
  --num_envs 16
```

**说明**：
- `--load_run` 指定要评估的训练运行
- 会加载 `./logs/rsl_rl/desktop_organizer/2026-01-24_10-30-22/model_final.pt`

---

## 🔍 常见问题

### Q1: 如何找到最新的训练运行？

```bash
# 方法 1：按时间排序
ls -lt ./logs/rsl_rl/desktop_organizer/

# 方法 2：只显示最新的
ls -lt ./logs/rsl_rl/desktop_organizer/ | head -2
```

---

### Q2: Resume 训练会覆盖原始模型吗？

**不会**！Resume 会创建**新的时间戳文件夹**，原始训练运行不会被修改。

```
logs/rsl_rl/desktop_organizer/
├── 2026-01-23_17-58-10/    ← 原始训练 [保留不变]
└── 2026-01-27_19-30-15/    ← Resume 训练 [新建文件夹]
```

---

### Q3: 如何指定自定义日志目录？

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 4096 \
  --max_iterations 3000 \
  --log_dir /custom/path/to/logs \
  --headless
```

**结果**：
- 日志保存到 `/custom/path/to/logs/2026-01-27_19-30-15/`

---

### Q4: 如何删除旧的训练运行？

```bash
# 删除单个训练运行
rm -rf ./logs/rsl_rl/desktop_organizer/2026-01-23_17-58-10

# 删除所有训练运行（谨慎！）
rm -rf ./logs/rsl_rl/desktop_organizer/*
```

---

### Q5: 训练运行之间有什么区别？

| 属性 | 从头训练 | Resume 训练 |
|------|---------|------------|
| **检查点加载** | 无 | 从指定运行加载 |
| **初始 iteration** | 0 | 从检查点的 iteration 继续 |
| **新建文件夹** | ✅ | ✅ |
| **覆盖原始运行** | N/A | ❌ 不覆盖 |

---

## 🎯 与官方 train.py 的对比

| 功能 | 官方 train.py | 修复后的 train_rl.py |
|------|--------------|-------------------|
| **动态时间戳文件夹** | ✅ | ✅ |
| **Resume 不覆盖** | ✅ | ✅ |
| **参数完全兼容** | ✅ | ✅ |
| **自动导入外部包** | ❌ | ✅ |

---

## 📝 修复记录

- **日期**：2026-01-27
- **问题**：每次训练覆盖同一个目录
- **修复**：添加动态时间戳文件夹生成
- **影响**：所有使用 `train_rl.py` 的训练任务
- **向后兼容**：✅ 完全兼容（只需确保 `--resume` 时提供 `--load_run`）

---

## ✅ 验证测试

### 测试 1：从头训练（创建新文件夹）

```bash
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 512 \
  --max_iterations 10 \
  --headless

# 预期：创建新的时间戳文件夹
ls -la ./logs/rsl_rl/desktop_organizer/
# 应该看到新的文件夹，格式为 YYYY-MM-DD_HH-MM-SS
```

### 测试 2：Resume 训练（不覆盖原始文件夹）

```bash
# 获取第一次训练的运行 ID
FIRST_RUN=$(ls -t ./logs/rsl_rl/desktop_organizer/ | head -1)
echo "第一次训练运行: $FIRST_RUN"

# Resume 训练
./isaaclab.sh -p /root/isaaclab-desktop-organizer/scripts/train_rl.py \
  --num_envs 512 \
  --max_iterations 20 \
  --resume \
  --load_run $FIRST_RUN \
  --headless

# 预期：创建新的时间戳文件夹，原始文件夹不变
ls -la ./logs/rsl_rl/desktop_organizer/
# 应该看到 2 个文件夹（原始 + Resume）
```

---

**🎉 修复完成！现在 `train_rl.py` 的行为与官方 `train.py` 完全一致了！**
