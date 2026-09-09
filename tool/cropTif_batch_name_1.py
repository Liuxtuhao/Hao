import cv2
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import os

# ==========================
# 参数配置
# ==========================
ROOT_DIR = r"E:\date\20260904"
OUTPUT_ROOT = r"E:\date\20260904\1"

NUM_SPLITS = 850# 沿长边切分的份数
THREADS = 12# 🌟 I/O密集型任务，写入压力大时建议先从 4 开始测试，不要盲目开大
USE_GRAYSCALE = True  # 强制转为灰度图读取

# 🌟 核心优化 1：关闭 OpenCV 内部的并行，防止与 Python 线程池冲突
cv2.setNumThreads(0)

# ==========================
# 收集所有 tif（递归）
# ==========================
def collect_tifs(root_dir):
    root = Path(root_dir)
    tif_list = list(root.rglob("*.tif"))
    print(f"扫描完成，共找到 {len(tif_list)} 个 tif")
    return tif_list


# ==========================
# 自适应方向切片
# ==========================
def split_image_adaptive(img, num_splits):
    h, w = img.shape[:2]
    
    if h >= w:
        direction = "vertical"
        max_len = h
    else:
        direction = "horizontal"
        max_len = w

    if num_splits > max_len:
        num_splits = max_len

    indices = np.linspace(0, max_len, num_splits + 1, dtype=int)

    for i in range(num_splits):
        start = indices[i]
        end = indices[i + 1]
        
        if direction == "vertical":
            sub = img[start:end, :]
        else:
            sub = img[:, start:end]
            
        yield i, sub


# ==========================
# 处理单个 tif
# ==========================
def process_tif(tif_path, output_root):
    try:
        read_mode = cv2.IMREAD_GRAYSCALE if USE_GRAYSCALE else cv2.IMREAD_UNCHANGED
        img = cv2.imread(str(tif_path), read_mode)

        if img is None:
            print(f"❌ 读取失败: {tif_path}")
            return

        parent_name = tif_path.parent.name
        tif_name = tif_path.stem

        out_dir = Path(output_root) / parent_name / tif_name
        out_dir.mkdir(parents=True, exist_ok=True)

        # 预先准备好通用的写入参数，提高循环效率
        encode_params = [cv2.IMWRITE_PNG_COMPRESSION, 0]

        for i, sub in split_image_adaptive(img, NUM_SPLITS):
            out_path = out_dir / f"{i:04d}.png"
            cv2.imwrite(str(out_path), sub, encode_params)

        print(f"✅ 处理完成: {parent_name} / {tif_path.name} (尺寸: {img.shape[1]}x{img.shape[0]})")

    except Exception as e:
        print(f"❌ 异常: {tif_path} | {e}")


# ==========================
# 主流程
# ==========================
def main():
    tif_list = collect_tifs(ROOT_DIR)
    if not tif_list:
        print("未找到任何 .tif 文件，退出。")
        return

    # 排序，让输出日志稍微好看一点
    tif_list = sorted(tif_list, key=lambda x: (x.parent.name, x.name))

    print(f"🚀 开始多线程处理（总计 {len(tif_list)} 个文件，线程数: {THREADS}）...")

    # 🌟 核心优化 2：将所有文件直接打平扔进线程池，不再按目录循环阻塞
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        # 使用 submit 或 map 均可，这里用 map 直接把整个任务链跑起来
        # 注意：不要在外部加 list() 强行阻塞，让线程池自己流动起来
        executor.map(lambda tif: process_tif(tif, OUTPUT_ROOT), tif_list)

    print("\n🎉 全部完成！")


if __name__ == "__main__":
    main()