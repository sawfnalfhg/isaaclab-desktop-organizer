#!/usr/bin/env python3
"""
为 MimicGen 生成的数据集添加训练/验证分割标记 (mask 字段)。

Robomimic 训练需要数据集包含 mask 字段来区分训练集和验证集。
MimicGen 生成的数据集默认不包含这些字段，需要手动添加。

Usage:
    python scripts/bc/add_mask.py --dataset ./datasets/generated.hdf5 --train_ratio 0.8
"""

import argparse
import h5py
import numpy as np


def add_mask_to_dataset(dataset_path: str, train_ratio: float = 0.8):
    """
    为 HDF5 数据集添加 mask 字段。

    Args:
        dataset_path: 数据集路径
        train_ratio: 训练集比例 (默认 0.8，即 80% 训练，20% 验证)
    """
    print(f"正在处理数据集: {dataset_path}")

    with h5py.File(dataset_path, 'r+') as f:
        # 获取所有演示
        demos = list(f['data'].keys())
        total_demos = len(demos)
        train_count = int(total_demos * train_ratio)

        print(f"\n数据集信息:")
        print(f"  总演示数: {total_demos}")
        print(f"  训练集: {train_count} ({train_ratio*100:.0f}%)")
        print(f"  验证集: {total_demos - train_count} ({(1-train_ratio)*100:.0f}%)")

        # 为每个 demo 添加 mask 字段
        print("\n正在添加 mask 字段...")
        for i, demo_name in enumerate(demos):
            demo = f[f'data/{demo_name}']

            # 删除旧的 mask（如果存在）
            if 'mask' in demo:
                del demo['mask']

            # 创建新的 mask: 1=训练集, 0=验证集
            mask_data = np.array([1 if i < train_count else 0], dtype=np.int8)
            demo.create_dataset('mask', data=mask_data)

            if (i + 1) % 10 == 0 or i == total_demos - 1:
                print(f"  进度: {i+1}/{total_demos}")

        # 创建根目录的 mask 分组
        print("\n正在创建 mask 分组...")
        if 'mask' not in f:
            f.create_group('mask')

        # 分割训练集和验证集
        train_demos = [d.encode('utf-8') for d in demos[:train_count]]
        valid_demos = [d.encode('utf-8') for d in demos[train_count:]]

        # 删除旧的 filter keys（如果存在）
        if 'train' in f['mask']:
            del f['mask/train']
        if 'valid' in f['mask']:
            del f['mask/valid']

        # 创建新的 filter keys
        f.create_dataset('mask/train', data=np.array(train_demos, dtype='S'))
        f.create_dataset('mask/valid', data=np.array(valid_demos, dtype='S'))

        print("\n✅ Mask 字段添加完成!")
        print(f"   训练集演示: {len(train_demos)}")
        print(f"   验证集演示: {len(valid_demos)}")
        print(f"\n现在可以使用该数据集进行 Robomimic 训练了。")


def main():
    parser = argparse.ArgumentParser(description="为数据集添加 mask 字段")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="数据集路径 (HDF5 文件)"
    )
    parser.add_argument(
        "--train_ratio",
        type=float,
        default=0.8,
        help="训练集比例 (默认 0.8)"
    )

    args = parser.parse_args()

    # 验证参数
    if not (0.0 < args.train_ratio < 1.0):
        raise ValueError(f"train_ratio 必须在 (0, 1) 范围内，当前值: {args.train_ratio}")

    # 添加 mask
    add_mask_to_dataset(args.dataset, args.train_ratio)


if __name__ == "__main__":
    main()
