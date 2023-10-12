from flask import Flask
import os.path

import cv2
import pymysql
from flask import Flask, request, session, redirect,send_file
from flask import render_template
from flask_bootstrap import Bootstrap
from openpyxl.styles import Alignment
from werkzeug.utils import secure_filename
import shutil
from gevent import pywsgi
import vtk
from trimesh.exchange.obj import export_obj
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import SimpleITK as sitk
import os

app = Flask(__name__)


def segment_and_save(input_path, output_dir):
    # 读取输入的 .nii.gz 文件
    image = sitk.ReadImage(input_path)
    # 获取图像数组和元数据
    image_array = sitk.GetArrayFromImage(image)
    spacing = image.GetSpacing()
    origin = image.GetOrigin()
    # 获取图像中不同的体素值
    unique_values = set(image_array.flatten())
    # 对每个体素值进行分割和保存
    for value in unique_values:
        if value == 0:  # 忽略背景（假设背景值为0）
            continue
        # 创建只包含当前体素值的二值图像
        segmented_array = (image_array == value).astype(image_array.dtype)
        # 创建新的 SimpleITK 图像对象
        segmented_image = sitk.GetImageFromArray(segmented_array)
        segmented_image.SetSpacing(spacing)
        segmented_image.SetOrigin(origin)
        # 构建输出文件路径
        output_filename = os.path.join(output_dir, f"segmented_value_{value}.nii.gz")
        # 保存分割后的图像
        sitk.WriteImage(segmented_image, output_filename)
        print(f"Segmented value {value} saved as {output_filename}")

@app.route('/',methods=['GET','POST'])
def scoring():  # put application's code here
    if request.method=='GET':
        # 输入文件路径和输出文件夹路径
        input_file_path = "static/0f593c1e-4bb8-470f-a87b-fee3dbd3b3ed.nii.gz"
        output_directory = "static/segmented_output"
        # 确保输出文件夹存在
        os.makedirs(output_directory, exist_ok=True)
        # 调用函数进行分割和保存
        segment_and_save(input_file_path, output_directory)
        return 'Hello World!'
    if request.method=='POST':
        return 'hi world'


if __name__ == '__main__':
    app.run()
