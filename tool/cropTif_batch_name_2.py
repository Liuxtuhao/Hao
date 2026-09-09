import cv2
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import os
from PIL import Image
import tifffile

# ==========================
# 核心优化：解决OpenCV大图限制
# ==========================
# 方法1：设置环境变量，禁用OpenCV的大小检查
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(pow(2, 40))  # 约1万亿像素

# ==========================
# 参数配置
# ==========================
ROOT_DIR = r"E:\z"
OUTPUT_ROOT = r"E:\z"

NUM_SPLITS = 1000  # 沿长边切分的份数
THREADS = 12  # I/O密集型任务
USE_GRAYSCALE = True  # 强制转为灰度图读取
USE_TIFFFILE_FALLBACK = True  # 当OpenCV失败时，尝试用tifffile读取

# 关闭 OpenCV 内部的并行
cv2.setNumThreads(0)


# ==========================
# 收集所有 tif（递归）
# ==========================
def collect_tifs(root_dir):
    root = Path(root_dir)
    tif_list = list(root.rglob("*.tif")) + list(root.rglob("*.tiff"))
    print(f"扫描完成，共找到 {len(tif_list)} 个 tif")
    return tif_list


# ==========================
# 安全读取图片（带降级方案）
# ==========================
def safe_read_image(tif_path):
    """尝试多种方法读取超大TIFF"""
    img = None
    used_method = "None"

    # 方法1：OpenCV（先尝试，速度快）
    try:
        read_mode = cv2.IMREAD_GRAYSCALE if USE_GRAYSCALE else cv2.IMREAD_UNCHANGED
        img = cv2.imread(str(tif_path), read_mode)
        if img is not None:
            used_method = "OpenCV"
            return img, used_method
    except Exception as e:
        print(f"⚠️ OpenCV读取失败，尝试备用方案: {e}")

    # 方法2：PIL/Pillow（适合大图，但内存占用较高）
    try:
        from PIL import Image
        pil_img = Image.open(tif_path)

        # 如果强制灰度
        if USE_GRAYSCALE:
            pil_img = pil_img.convert('L')  # 转灰度
        else:
            # 保持原始模式，如果是RGBA转RGB
            if pil_img.mode == 'RGBA':
                pil_img = pil_img.convert('RGB')

        # 转为numpy数组
        img = np.array(pil_img)

        # 如果是彩色图，需要转BGR供OpenCV使用（后面保存时不需要，但为了兼容）
        # 但实际上我们后面只保存，不需要转换回BGR
        used_method = "PIL"
        print(f"📷 使用PIL读取成功: {tif_path.name}")
        return img, used_method

    except Exception as e:
        print(f"⚠️ PIL读取失败: {e}")

    # 方法3：tifffile（专门处理TIFF，最稳健）
    if USE_TIFFFILE_FALLBACK:
        try:
            import tifffile

            # 读取时直接指定模式
            if USE_GRAYSCALE:
                img = tifffile.imread(tif_path, key=0)  # 读取第一页
                # 如果是彩色图，转为灰度
                if len(img.shape) == 3 and img.shape[2] in [3, 4]:
                    # 简单的灰度转换（Y = 0.299R + 0.587G + 0.114B）
                    img = np.dot(img[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            else:
                img = tifffile.imread(tif_path, key=0)

            used_method = "tifffile"
            print(f"📷 使用tifffile读取成功: {tif_path.name}")
            return img, used_method

        except Exception as e:
            print(f"⚠️ tifffile读取失败: {e}")

    return None, "Failed"


# ==========================
# 自适应方向切片（优化版）
# ==========================
def split_image_adaptive(img, num_splits):
    h, w = img.shape[:2]

    # 对于超大图，打印尺寸信息
    total_pixels = h * w
    if total_pixels > 100000000:  # 1亿像素
        print(f"   📐 超大图: {w}x{h} = {total_pixels / 1000000:.1f}M 像素")

    if h >= w:
        direction = "vertical"
        max_len = h
    else:
        direction = "horizontal"
        max_len = w

    if num_splits > max_len:
        num_splits = max_len
        print(f"   ⚠️ 切分数超过图片尺寸，调整为 {num_splits}")

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
# 处理单个 tif（增强版）
# ==========================
def process_tif(tif_path, output_root):
    try:
        # 安全读取图片
        img, method = safe_read_image(tif_path)

        if img is None:
            print(f"❌ 所有读取方法均失败: {tif_path}")
            return

        # 检查图像维度
        if len(img.shape) == 2:
            h, w = img.shape
            channels = 1
        else:
            h, w = img.shape[:2]
            channels = img.shape[2] if len(img.shape) > 2 else 1

        # 创建输出目录
        parent_name = tif_path.parent.name
        tif_name = tif_path.stem
        out_dir = Path(output_root) / parent_name / tif_name
        out_dir.mkdir(parents=True, exist_ok=True)

        # 预先准备PNG编码参数
        encode_params = [cv2.IMWRITE_PNG_COMPRESSION, 0]  # 0=无压缩，速度最快

        # 切片并保存
        slice_count = 0
        total_slices = min(NUM_SPLITS, max(h, w))

        for i, sub in split_image_adaptive(img, NUM_SPLITS):
            out_path = out_dir / f"{i:04d}.png"
            cv2.imwrite(str(out_path), sub, encode_params)
            slice_count += 1

            # 每100片打印一次进度
            if (i + 1) % 100 == 0:
                print(f"   📊 切片进度: {i + 1}/{total_slices}")

        # 成功信息
        size_info = f"{w}x{h}" if channels == 1 else f"{w}x{h}x{channels}"
        print(f"✅ {tif_path.parent.name}/{tif_path.name} [{size_info}] 读取方式:{method} 切片:{slice_count}张")

    except MemoryError as e:
        print(f"❌ 内存不足: {tif_path} | {e}")
        print(f"   💡 建议：减少NUM_SPLITS或使用分块读取")
    except Exception as e:
        print(f"❌ 异常: {tif_path} | {e}")


# ==========================
# 主流程（增强版）
# ==========================
def main():
    print("=" * 60)
    print("🔧 TIFF大图切片工具")
    print("=" * 60)

    # 打印配置
    print(f"📁 输入目录: {ROOT_DIR}")
    print(f"📁 输出目录: {OUTPUT_ROOT}")
    print(f"✂️  切分数: {NUM_SPLITS}")
    print(f"🧵 线程数: {THREADS}")
    print(f"🎯 灰度模式: {USE_GRAYSCALE}")
    print(f"📷 备用读取: {USE_TIFFFILE_FALLBACK}")
    print("=" * 60)

    # 收集文件
    tif_list = collect_tifs(ROOT_DIR)
    if not tif_list:
        print("❌ 未找到任何 .tif/.tiff 文件，退出。")
        return

    # 按文件大小排序（从小到到大），避免一开始就卡住
    tif_list = sorted(tif_list, key=lambda x: x.stat().st_size)
    print(
        f"📊 文件大小范围: {tif_list[0].stat().st_size / 1024 / 1024:.1f}MB ~ {tif_list[-1].stat().st_size / 1024 / 1024:.1f}MB")

    print(f"🚀 开始多线程处理（总计 {len(tif_list)} 个文件，线程数: {THREADS}）...")
    print("=" * 60)

    # 使用线程池处理
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        # 提交所有任务
        futures = []
        for tif_path in tif_list:
            future = executor.submit(process_tif, tif_path, OUTPUT_ROOT)
            futures.append(future)

        # 等待所有任务完成
        for future in futures:
            try:
                future.result()  # 如果有异常会在这里抛出
            except Exception as e:
                print(f"❌ 线程任务异常: {e}")

    print("\n" + "=" * 60)
    print("🎉 全部完成！")


if __name__ == "__main__":
    main()