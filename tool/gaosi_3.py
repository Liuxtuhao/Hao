import cv2

input_path = r"0906.png"
output_path = r"denoised_nlm.png"

gray = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

if gray is None:
    raise FileNotFoundError(f"无法读取图片：{input_path}")

# 第一次：去除主要颗粒
denoised_1 = cv2.fastNlMeansDenoising(
    gray,
    None,
    h=8,
    templateWindowSize=7,
    searchWindowSize=21
)

# 第二次：轻度去除残余颗粒
denoised_2 = cv2.fastNlMeansDenoising(
    denoised_1,
    None,
    h=4,
    templateWindowSize=7,
    searchWindowSize=21
)

# 轻度锐化恢复轮廓
blur = cv2.GaussianBlur(denoised_2, (0, 0), sigmaX=0.8)

result = cv2.addWeighted(
    denoised_2, 1.3,
    blur, -0.3,
    0
)

cv2.imwrite(output_path, denoised_2)

print(f"完成：{output_path}")
