from pathlib import Path


def rename_images_from_1(folder_path: str):
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        print(f"文件夹不存在: {folder}")
        return

    image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

    image_files = sorted(
        [
            p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in image_extensions
        ],
        key=lambda p: p.name
    )

    if not image_files:
        print("没有找到图片文件")
        return

    print(f"找到 {len(image_files)} 张图片")

    # 第一步：先改为临时名称，避免 1.png、2.png 等文件名冲突
    temp_files = []

    for i, old_path in enumerate(image_files, start=1):
        temp_path = folder / f"__temp_rename_{i}__{old_path.suffix.lower()}"

        old_path.rename(temp_path)
        temp_files.append(temp_path)

    # 第二步：改为 1.png、2.png、3.png ...
    for i, temp_path in enumerate(temp_files, start=1):
        new_path = folder / f"{i}{temp_path.suffix.lower()}"

        temp_path.rename(new_path)

        print(f"{temp_path.name} -> {new_path.name}")

    print("重命名完成")


if __name__ == "__main__":
    rename_images_from_1(
        r"C:\Users\Lenovo\Desktop\EntryClassify\0"
    )
