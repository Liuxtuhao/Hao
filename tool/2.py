from pathlib import Path
import shutil

src_root = Path(r"D:\data\0716\Organized_by_Number_Results")
dst_root = Path(r"C:\Users\Lenovo\Desktop\20260729RValNG")

# 需要复制的文件后缀
target_exts = {".jpg", ".json"}

for src_dir in src_root.iterdir():
    # 只处理文件夹
    if not src_dir.is_dir():
        continue

    folder_name = src_dir.name
    dst_dir = dst_root / folder_name

    # 创建目标文件夹
    dst_dir.mkdir(parents=True, exist_ok=True)

    # 遍历当前子文件夹中的文件
    for file_path in src_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in target_exts:
            dst_file = dst_dir / file_path.name
            shutil.copy2(file_path, dst_file)
            print(f"复制: {file_path} -> {dst_file}")

print("全部处理完成。")
