from pathlib import Path
import cv2


def crop_images_by_tool_radius(
    input_dir: str,
    save_dir: str,
    tool_radius_um: float,
    pxl2um: float,
    default_width: int = 175,
):
    """
    批量读取 input_dir 内图像，以图像中心为中心裁剪 ROI，并保存到 save_dir。

    参数：
        input_dir: 输入图片目录
        save_dir: 裁剪结果保存目录
        tool_radius_um: 工具半径，单位 um
        pxl2um: 像素尺寸，单位 um/px
        default_width: 未设置工具半径时的默认半宽
    """

    input_path = Path(input_dir)
    output_path = Path(save_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 支持的图像后缀
    image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

    image_paths = sorted([
        p for p in input_path.iterdir()
        if p.is_file() and p.suffix.lower() in image_extensions
    ])

    if not image_paths:
        print(f"未找到图像: {input_dir}")
        return

    print(f"图像数量: {len(image_paths)}")

    for i, image_path in enumerate(image_paths):
        img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

        if img is None:
            print(f"读取失败，跳过: {image_path}")
            continue

        height, width_img = img.shape[:2]

        # 对应 C++：
        # Point center = Point(cols / 2, rows / 2);
        center_x = width_img // 2
        center_y = height // 2

        # 对应 C++：
        # int width = 175;
        roi_half_width = default_width

        # 对应：
        # if (fToolRadiusInUm > 0.1)
        # {
        #     fRadiusInPxl = fToolRadiusInUm / fPxl2um;
        #     width = fRadiusInPxl * 3;
        # }
        if tool_radius_um > 0.1 and pxl2um > 0:
            radius_in_pxl = tool_radius_um / pxl2um
            roi_half_width = int(radius_in_pxl * 3)

        # 对应：
        # roi = domain & roi;
        # 防止 ROI 超出图像范围
        x1 = max(0, center_x - roi_half_width)
        y1 = max(0, center_y - roi_half_width)
        x2 = min(width_img, center_x + roi_half_width)
        y2 = min(height, center_y + roi_half_width)

        if x1 >= x2 or y1 >= y2:
            print(f"ROI 无效，跳过: {image_path.name}")
            continue

        # OpenCV/Python 裁剪格式：[y1:y2, x1:x2]
        img_crop = img[y1:y2, x1:x2].copy()

        # 保留原文件名；也可以使用 f"{i}.png"
        output_file = output_path / image_path.name

        success = cv2.imwrite(str(output_file), img_crop)

        if success:
            print(
                f"[{i}] 保存成功: {output_file.name}, "
                f"原图={width_img}x{height}, "
                f"ROI=({x1}, {y1}, {x2 - x1}, {y2 - y1})"
            )
        else:
            print(f"[{i}] 保存失败: {output_file}")


if __name__ == "__main__":
    crop_images_by_tool_radius(
        input_dir=r"C:\Users\Lenovo\Desktop\All\00557\AD5666AA_9010_3681359106012-T08C582Copper-00557",
        save_dir=r"C:\Users\Lenovo\Desktop\2",
        tool_radius_um=200.0,   # 对应 fToolRadiusInUm
        pxl2um=6.5453086,       # 对应 fPxl2um
        default_width=175
    )
