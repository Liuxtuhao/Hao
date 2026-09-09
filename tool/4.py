import os
import shutil

json_dir = r"C:\Users\Lenovo\Desktop\0729\json"
folder_root = r"C:\Users\Lenovo\Desktop\0729\20260729RValNG"

# 获取 json 文件
json_files = [
    f for f in os.listdir(json_dir)
    if f.lower().endswith(".json")
]

# 获取目标目录下的文件夹
folders = [
    f for f in os.listdir(folder_root)
    if os.path.isdir(os.path.join(folder_root, f))
]

# 排序，保证一一对应
json_files.sort()
folders.sort()

print("json文件数量:", len(json_files))
print("文件夹数量:", len(folders))

# 数量检查
if len(json_files) != len(folders):
    print("警告：json文件数量和文件夹数量不一致！")
    print("将按较少的数量进行处理。")

count = min(len(json_files), len(folders))

for i in range(count):
    json_name = json_files[i]
    folder_name = folders[i]

    old_json_path = os.path.join(json_dir, json_name)
    target_folder = os.path.join(folder_root, folder_name)

    # 新 json 名字 = 文件夹名.json
    new_json_name = folder_name + ".json"
    new_json_path = os.path.join(target_folder, new_json_name)

    # 如果目标文件已存在，避免覆盖
    # if os.path.exists(new_json_path):
    #     print("目标文件已存在，跳过:", new_json_path)
    #     continue

    shutil.move(old_json_path, new_json_path)

    print(f"移动并重命名: {json_name}  ->  {folder_name}\\{new_json_name}")

print("完成！")
