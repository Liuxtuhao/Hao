import os
import shutil

src_dir = r"C:\Users\Lenovo\Desktop\1"
dst_dir = r"C:\Users\Lenovo\Desktop\20260721CopperMultiTopClassify\trace"

os.makedirs(dst_dir, exist_ok=True)

# 支持的图片格式
img_exts = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]

# 获取并排序图片
img_files = [
    f for f in os.listdir(src_dir)
    if os.path.splitext(f)[1].lower() in img_exts
]

img_files.sort()
start = 80
count = start

# 每隔10张抽1张，并重新编号
for idx, filename in enumerate(img_files):
    if idx % 1 == 0:
        src_path = os.path.join(src_dir, filename)

        # 获取原始扩展名
        ext = os.path.splitext(filename)[1].lower()

        # 重新编号，例如 0001.jpg
        new_name = f"{count:04d}{ext}"
        dst_path = os.path.join(dst_dir, new_name)

        shutil.copy2(src_path, dst_path)

        print(f"复制: {filename}  ->  {new_name}")

        count += 1



print("完成，共抽取", count -start, "张")
