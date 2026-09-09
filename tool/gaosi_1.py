from pathlib import Path
import cv2

# =========================================================
# 输入、输出文件夹
# =========================================================
input_dir = Path(r"E:\z\0001\0001\0909_15S-90kv-110un-15MAG_0-TEmptyS0-00001")
output_dir = Path(r"E:\z\0001\0001\0909_15S-90kv-110un-15MAG_0-TEmptyS0-00001")

# 是否递归处理子文件夹
RECURSIVE = False

# 支持的图片格式
image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

# =========================================================
# 检查输入目录
# =========================================================
if not input_dir.exists():
    raise FileNotFoundError(f"输入文件夹不存在：{input_dir}")

# 自动创建输出目录
output_dir.mkdir(parents=True, exist_ok=True)

# =========================================================
# 获取图片文件列表
# =========================================================
if RECURSIVE:
    image_files = [
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in image_extensions
    ]
else:
    image_files = [
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in image_extensions
    ]

if not image_files:
    raise FileNotFoundError(f"在该目录下未找到图片：{input_dir}")

print(f"共找到 {len(image_files)} 张图片，开始 NLM 去噪...\n")

# =========================================================
# 批量处理
# =========================================================
success_count = 0
fail_count = 0

for index, input_path in enumerate(image_files, start=1):

    try:
        # 以灰度方式读取图片
        gray = cv2.imread(str(input_path), cv2.IMREAD_GRAYSCALE)

        if gray is None:
            raise ValueError("OpenCV 无法读取该图片")

        # 非局部均值去噪
        denoised = cv2.fastNlMeansDenoising(
            gray,
            None,
            h=6,
            templateWindowSize=7,
            searchWindowSize=21
        )

        # 输出文件名：
        # 例如 0516.png -> 0516_nlm.png
        output_name = f"{input_path.stem}_nlm.png"
        output_path = output_dir / output_name

        # 保存结果
        saved = cv2.imwrite(str(output_path), denoised)

        if not saved:
            raise IOError("图片保存失败")

        success_count += 1
        print(f"[{index}/{len(image_files)}] 完成：{input_path.name} -> {output_path.name}")

    except Exception as e:
        fail_count += 1
        print(f"[{index}/{len(image_files)}] 失败：{input_path.name}，原因：{e}")

print("\n" + "=" * 60)
print("批量处理结束")
print(f"成功：{success_count} 张")
print(f"失败：{fail_count} 张")
print(f"输出目录：{output_dir}")
print("=" * 60)
