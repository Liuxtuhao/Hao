import cv2


def gaussian_canny(image_path: str, output_path: str):
    # 以灰度模式读取图片
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if gray is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")

    # 高斯滤波，减少噪声
    img = cv2.GaussianBlur(gray, (3, 3), 0)

    # Canny 边缘检测
    canny = cv2.Canny(img, 50, 150)

    # 保存边缘图
    success = cv2.imwrite(output_path, canny)

    if not success:
        raise IOError(f"保存失败: {output_path}")

    # 显示结果
    cv2.imshow("gray", gray)
    cv2.imshow("gaussian blur", img)
    cv2.imshow("canny", canny)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    gaussian_canny(
        image_path=r"D:\test\imgCircleFob\src\10\30.png",
        output_path=r"C:\Users\Lenovo\Desktop\canny.png",
    )
