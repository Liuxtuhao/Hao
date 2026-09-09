import cv2

input_path = r"0906.png"
output_path = "denoised_nlm.png"

# 读取灰度图
gray = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

if gray is None:
    raise FileNotFoundError(f"无法读取图片：{input_path}")

# 非局部均值去噪
denoised = cv2.fastNlMeansDenoising(
    gray,
    None,
    h=8,                   # 去噪强度，建议从 4~8 开始
    templateWindowSize=7,  # 模板窗口，通常使用 7
    searchWindowSize=21    # 搜索窗口，通常使用 21
)

cv2.imwrite(output_path, denoised)
print(f"去噪完成：{output_path}")
