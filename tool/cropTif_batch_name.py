import cv2
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# ==========================
# 参数配置
# ==========================
ROOT_DIR = r"E:\date\20260905\tif"
OUTPUT_ROOT = r"E:\date\20260905\1"

NUM_SPLITS = 1000
THREADS = 12
USE_GRAYSCALE = True

IMAGE_EXTS = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp"}

cv2.setNumThreads(0)


# ==========================
# 收集所有图片
# ==========================
def collect_images(root_dir):
    root = Path(root_dir)

    image_list = [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]

    print(f"扫描完成，共找到 {len(image_list)} 张图片")
    return image_list


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
# 处理单张图片
# ==========================
def process_image(img_path, output_root):
    try:
        read_mode = cv2.IMREAD_GRAYSCALE if USE_GRAYSCALE else cv2.IMREAD_UNCHANGED
        img = cv2.imread(str(img_path), read_mode)

        if img is None:
            print(f"❌ 读取失败: {img_path}")
            return

        img_path = Path(img_path)

        # 获取图片所在的直接父文件夹名字
        # 例如：D:\data\0716\Organized_by_Number\00057\xxx.tif
        # parent_folder_name = 00057
        parent_folder_name = img_path.parent.name

        # 图片名，不带后缀
        img_name = img_path.stem

        # 输出路径：
        # C:\Users\Lenovo\Desktop\20260729RValNG\00057\图片名\
        out_dir = Path(output_root) / parent_folder_name / img_name
        out_dir.mkdir(parents=True, exist_ok=True)

        encode_params = [cv2.IMWRITE_PNG_COMPRESSION, 0]

        for i, sub in split_image_adaptive(img, NUM_SPLITS):
            out_path = out_dir / f"{i:04d}.png"
            cv2.imwrite(str(out_path), sub, encode_params)

        print(
            f"✅ 处理完成: {parent_folder_name} / {img_path.name} "
            f"(尺寸: {img.shape[1]}x{img.shape[0]})"
        )

    except Exception as e:
        print(f"❌ 异常: {img_path} | {e}")


# ==========================
# 主流程
# ==========================
def main():
    image_list = collect_images(ROOT_DIR)

    if not image_list:
        print("未找到任何图片文件，退出。")
        return

    image_list = sorted(image_list, key=lambda x: (x.parent.name, x.name))

    print(
        f"🚀 开始多线程处理，总计 {len(image_list)} 张图片，"
        f"线程数: {THREADS}"
    )

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(lambda img: process_image(img, OUTPUT_ROOT), image_list)

    print("\n🎉 全部完成！")


if __name__ == "__main__":
    main()
