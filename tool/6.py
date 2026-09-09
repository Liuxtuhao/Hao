from pathlib import Path
import cv2


def crop_images_by_tool_radius(
    input_dir: Path,
    save_dir: Path,
    tool_radius_um: float,
    pxl2um: float,
    default_width: int = 175,
):
    """处理单个图像文件夹：中心裁剪后保存。"""

    save_dir.mkdir(parents=True, exist_ok=True)

    image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

    image_paths = sorted(
        [
            p for p in input_dir.iterdir()
            if p.is_file() and p.suffix.lower() in image_extensions
        ],
        key=lambda p: p.name
    )

    if not image_paths:
        print(f"  未找到图像，跳过: {input_dir}")
        return 0

    success_count = 0

    for i, image_path in enumerate(image_paths):
        img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

        if img is None:
            print(f"  读取失败，跳过: {image_path}")
            continue

        height, width_img = img.shape[:2]

        # 图像中心
        center_x = width_img // 2
        center_y = height // 2

        # ROI 半宽
        roi_half_width = default_width

        if tool_radius_um > 0.1 and pxl2um > 0:
            radius_in_pxl = tool_radius_um / pxl2um
            roi_half_width = int(radius_in_pxl * 2)

        # 防止 ROI 超出图像范围
        x1 = max(0, center_x - roi_half_width)
        y1 = max(0, center_y - roi_half_width)
        x2 = min(width_img, center_x + roi_half_width)
        y2 = min(height, center_y + roi_half_width)

        if x1 >= x2 or y1 >= y2:
            print(f"  ROI 无效，跳过: {image_path.name}")
            continue

        # 裁剪
        img_crop = img[y1:y2, x1:x2].copy()

        # 保存时保留原始文件名
        output_file = save_dir / image_path.name

        if cv2.imwrite(str(output_file), img_crop):
            success_count += 1
        else:
            print(f"  保存失败: {output_file}")

    print(
        f"  完成：{success_count}/{len(image_paths)} 张，"
        f"输出目录：{save_dir}"
    )

    return success_count


def batch_crop_folders(
    root_input_dir: str,
    root_output_dir: str,
    tool_radius_um: float,
    pxl2um: float,
    default_width: int = 150
):
    """
    批量处理 root_input_dir 下所有子文件夹。

    每一个子文件夹的输出，保存至 root_output_dir 下的同名文件夹。
    """

    root_input_path = Path(root_input_dir)
    root_output_path = Path(root_output_dir)

    if not root_input_path.exists():
        print(f"输入总目录不存在: {root_input_path}")
        return

    root_output_path.mkdir(parents=True, exist_ok=True)

    # 找到所有一级子目录
    input_folders = sorted(
        [p for p in root_input_path.iterdir() if p.is_dir()],
        key=lambda p: p.name
    )

    if not input_folders:
        print(f"没有找到子文件夹: {root_input_path}")
        return

    print(f"共找到 {len(input_folders)} 个待处理文件夹")

    total_images = 0

    for folder_index, input_folder in enumerate(input_folders, start=1):
        # 输出目录保持相同的子文件夹名称
        output_folder = root_output_path / input_folder.name

        print(
            f"\n[{folder_index}/{len(input_folders)}] "
            f"处理文件夹: {input_folder.name}"
        )

        count = crop_images_by_tool_radius(
            input_dir=input_folder,
            save_dir=output_folder,
            tool_radius_um=tool_radius_um,
            pxl2um=pxl2um,
            default_width=default_width,
        )

        total_images += count

    print("\n========== 批量处理结束 ==========")
    print(f"成功保存图像总数: {total_images}")
    print(f"输出总目录: {root_output_path}")


if __name__ == "__main__":
    batch_crop_folders(
        # 总输入目录，里面包含多个待处理图像文件夹
        root_input_dir=r"C:\Users\Lenovo\Desktop\All",

        # 总输出目录；每个输入子目录会在这里生成同名目录
        root_output_dir=r"C:\Users\Lenovo\Desktop\2",

        tool_radius_um=175.0,
        pxl2um=6.5453086,
        default_width=175,
    )
