'''
将label中标注的json文件，转化为可用于分割训练的标签二值化黑白png图片
'''
import os
import cv2
import numpy as np
import shutil
import glob

# def json_png():  第一次转换用到
path_json = r'C:\Users\Lenovo\Desktop\seg'  # 这里是指.json文件所在文件夹的路径
                             # 批量转换，修改此路径
                             # 此路径为，json文件所在路径
# def extract_png():  第二次转换用到
path_json_to_data = os.path.join(path_json,"json_data")  # json文件夹所在位置
path_save_png = os.path.join(path_json,"json_png")  # 将标签图从json文件中批量取出后指定保存的文件目录
path_save_png_binary = os.path.join(path_json,"json_png_binary")       #二至图像最终保存的路径
def pre_treatment():
    '''
    创建三个文件夹用于存储
    json_data用于存储json转换img.png     label.png    label_names.txt   label_viz.png的文件夹
    json_png用于存储从json_data提取出来的label。png（最终存储名字与json文件对应）
    json_png_binary 用于存储最终转换后的8位的单通道黑白图像
    :return:
    '''
    if os.path.isdir(os.path.join(path_json,"json_data")) is False:
        os.mkdir(os.path.join(path_json,"json_data"))
    else:
        print('文件已存在')
    if os.path.isdir(os.path.join(path_json,"json_png")) is False:
        os.mkdir(os.path.join(path_json,"json_png"))
    else:
        print('文件已存在')
    if os.path.isdir(os.path.join(path_json,"json_png_binary")) is False:
        os.mkdir(os.path.join(path_json,"json_png_binary"))
    else:
        print('文件已存在')

def json_png():
    '''
    批量将json转换为img.png     label.png    label_names.txt   label_viz.png
    并存储至当前文件夹下的json_date文件夹中
    :return: 无
    '''
    json_file = glob.glob(os.path.join(path_json, "*.json"))
    os.system("activate labelme")     #激活labelme环境（根据自己设置的修改）
    for file in json_file:
        os.system("labelme_json_to_dataset.exe %s" % (file))  #调用labelme，自带的程序进行批量转换
                                                              #labelme中\.conda\envs\labelme\Lib\site-packages\labelme\cli中的json_to_dataset.py被修改过
                                                            # 具体修改见json_to_dataset.py
def extract_png():
    '''
    将标签图从json转换后的文件夹中批量取出，
    并保证保存的png图片名和原json文件名一致
    '''
    for eachfile in os.listdir(path_json_to_data):
        path1 = os.path.join(path_json_to_data, eachfile)

        if os.path.isdir(path1):
            label_path = os.path.join(path1, 'label.png')

            if os.path.exists(label_path):
                # 去掉转换后文件夹名末尾的 _json
                # 例如：001_json -> 001
                # 例如：image_001_json -> image_001
                json_name = eachfile.replace('_json', '')

                save_name = json_name + '.png'
                save_path = os.path.join(path_save_png, save_name)

                shutil.copy(label_path, save_path)

                print(save_name + ' successfully moved')


def png_to_binary():
    '''
    由于数据集是做二分类分割，所以，需要将ground_truth转换为8位的单通道黑白图像，才能作为训练时的label使用。
    将提取出来的png转换为8位的单通道黑白图像
    '''
    for im in os.listdir(path_save_png):
        img = cv2.imread(os.path.join(path_save_png, im))
        b, g, r = cv2.split(img)
        r[np.where(r != 0)] = 255
        cv2.imwrite(os.path.join(path_save_png_binary, im), r)

def process():
    pre_treatment()    #预处理，创建存储所需的相应文件夹
    json_png()         #调用labelme的json转换png程序
    extract_png()      #从转换的数据中提取png图像
    png_to_binary()    #将png转换为8位的单通道黑白图像，用于分割训练


if __name__ == "__main__":
    process()