import os.path
import random

import cv2
import pymysql
from flask import Flask, request, session, redirect, send_file
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
import numpy as np

# 初始化Flask后端
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(5)
bootstrap = Bootstrap(app)

# 连接到数据库
cnn = pymysql.connect(host="frp-can.top", port=64563, user="root", password="oypjyozj", database="test", charset="utf8")
cursor = cnn.cursor()


@app.route('/', methods=['GET', 'POST'])
def grade():
    if request.method == 'GET':
        return render_template("grade.html", id='123123')
    if request.method == 'POST':
        f = request.files['image']
        student_ID = request.form.get("student_id")
        student_Name = request.form.get("student_name")
        base_path = os.path.dirname(__file__)
        print(base_path)
        # 检测用户名匹配
        cursor.execute("SELECT * FROM `student` WHERE student_id='" + student_ID + "'")
        result = cursor.fetchall()
        print(result)
        if result:
            for row in result:
                img_path = secure_filename(f.filename)
                print(img_path)
                dir_path = os.path.join(base_path, 'static/img/student_upload', student_ID)
                print(dir_path)
                upload_path = os.path.join(base_path, 'static/img/student_upload', student_ID, img_path)
                print(upload_path)
                # upload_path = upload_path.replaceAll("\\", "\\\\")

                if os.path.exists(dir_path):
                    f.save(upload_path)
                # print(upload_path)
                else:
                    os.mkdir(dir_path)
                    f.save(upload_path)
                print(upload_path)
                upload_path = upload_path.replace("\\", "/")
                number = random.randint(1, 100)
                sql = "INSERT INTO student_upload VALUES(" + student_ID + ",'" + student_Name + "','" + upload_path + "')"
                cursor.execute(sql)
                cursor.connection.commit()
                print(123132132132132132121213123213213)
                return "已上传成功"
        else:
            return "查无此人，请重新输入学生ID"


@app.route('/GT', methods=['GET', 'POST'])
def GT():
    if request.method == 'GET':
        return render_template("GTupdate.html", id='123123')
    if request.method == 'POST':
        f = request.files['image']
        base_path = os.path.dirname(__file__)
        print(base_path)
        img_path = secure_filename(f.filename)
        print(img_path)
        upload_path = os.path.join(base_path, 'static/img/GT', img_path)
        print(upload_path)
        # upload_path = upload_path.replaceAll("\\", "\\\\")
        f.save(upload_path)
        print(upload_path)
        print(123132132132132132121213123213213)
        return "已上传成功"


def compute_dice_coefficient(label1, label2):
    intersection = np.logical_and(label1, label2)
    dice_coefficient = (2.0 * np.sum(intersection)) / (np.sum(label1) + np.sum(label2))
    return dice_coefficient


@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if request.method == 'GET':
        # 现在对GT进行单器官剥离保存
        output_file_name = ['0.nii.gz', '1.nii.gz', '2.nii.gz', '3.nii.gz', '4.nii.gz', '5.nii.gz', '6.nii.gz',
                            '7.nii.gz', '8.nii.gz', '9.nii.gz', '10.nii.gz', '11.nii.gz', ]
        GT_file_path = "./static/img/GT/"
        output_GT_path = "./static/GT_output/"
        input_GT_names = os.listdir(GT_file_path)
        for i in input_GT_names:
            output_GT_filename = output_GT_path + str(i)[0] + str(i)[1] + str(i)[2] + str(i)[3] + str(i)[4]
            if os.path.exists(output_GT_filename):
                print("GT_filename存在")
            else:
                os.mkdir(output_GT_filename)  # 创好文件夹
        for i in input_GT_names:  # 再对每一个GT进行操作
            output_GT_filename = output_GT_path + str(i)[0] + str(i)[1] + str(i)[2] + str(i)[3] + str(i)[4] + "/"
            image = sitk.ReadImage(GT_file_path + i)  # 读取一个GT
            for P in range(1, 12):
                # 创建一个二值图像，只保留值为i的体素
                binary_image = sitk.BinaryThreshold(image, lowerThreshold=P, upperThreshold=P)  # 把一个GT分成12份nii
                sitk.WriteImage(binary_image, output_GT_filename + "/" + output_file_name[P])
        # 现在对学生上传文件进行单器官剥离保存
        cursor.execute("SELECT student_id FROM `student_upload`")
        result = cursor.fetchall()
        print(result)
        for num in result:
            for i in num:
                input_file_path = "./static/img/student_upload/" + str(i)
                output_path = "./static/segmented_output/" + str(i)
                if os.path.exists(output_path):
                    print("有")
                else:
                    os.mkdir(output_path)
                # 读取student_upload表中的所有.nii.gz文件
                input_file_names = os.listdir(input_file_path)
                for j in input_file_names:
                    k = "./static/img/student_upload/" + str(i) + "/" + str(j)
                    image = sitk.ReadImage(k)

                    for P in range(1, 12):
                        # 创建一个二值图像，只保留值为i的体素
                        binary_image = sitk.BinaryThreshold(image, lowerThreshold=P, upperThreshold=P)

                        # 将二值图像保存为.nii.gz文件
                        seperate_path_upper = output_path + "/" + str(j)[0] + str(j)[1] + str(j)[2] + str(j)[3] + \
                                              str(j)[4]
                        seperate_path = seperate_path_upper + "/" + output_file_name[P]
                        if os.path.exists(seperate_path_upper):
                            print("seperate_path_upper存在")
                        else:
                            os.mkdir(seperate_path_upper)
                            print("seperate_path_upper已建立")
                        sitk.WriteImage(binary_image, seperate_path)
                        print(seperate_path)

                    print("分割后的图像已保存。")
        # 现在开始对照GT图评学生上传文件的DICE总分和各器官小分
        for i in os.listdir("./static/GT_output"):
            for j in os.listdir("./static/segmented_output"):
                for k in os.listdir("./static/segmented_output/" + j):
                    if (i == k):
                        print(j + "同学" + "有" + i)
                        # 开始评分
                        Dice_Array = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float64)
                        for P in range(1, 12):
                            image_X = sitk.ReadImage(
                                "./static/segmented_output/" + j + "/" + i + "/" + str(P) + ".nii.gz")
                            image_Y = sitk.ReadImage("./static/GT_output/" + i + "/" + str(P) + ".nii.gz")

                            # Convert SimpleITK images to numpy arrays
                            data_X = sitk.GetArrayFromImage(image_X)
                            data_Y = sitk.GetArrayFromImage(image_Y)

                            # Assuming the labels you want to compare are binary masks
                            label_X = data_X > 0
                            label_Y = data_Y > 0

                            dice_coefficient = compute_dice_coefficient(label_X, label_Y)
                            print(f"{j}同学的{i}文件的{P}器官的Dice Coefficient: {dice_coefficient:.4f}")
                            print(type(dice_coefficient))
                            Dice_Array[P - 1] = dice_coefficient
                        # 现在已完成对j同学i文件p器官的dice计算，现在开始制作三张表：1：所有打分记录表(grade) 2：压缩包dice打分表(zip) 3：排行榜表(rank)
                        print(Dice_Array)
                        sql = f"INSERT INTO grade VALUES({random.randint(0, 99999999)},{j},'{i}',{Dice_Array[0]},{Dice_Array[1]},{Dice_Array[2]},{Dice_Array[3]}," \
                              f"{Dice_Array[4]},{Dice_Array[5]},{Dice_Array[6]},{Dice_Array[7]},{Dice_Array[8]},{Dice_Array[9]},{Dice_Array[10]},{Dice_Array.mean()})"
                        cursor.execute(sql)
                        cursor.connection.commit()
                        # grade表制作完成
        for j in os.listdir("./static/segmented_output"):
            goal_Sum = 0
            GT_num = len(os.listdir("./static/GT_output"))
            sql = f"SELECT * FROM `grade` where Student_ID={j} ORDER BY goal DESC"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            for i in os.listdir("./static/GT_output"):
                for iter in result:
                    if iter[2] == i:
                        print(f"{j}同学有{i}文件，分数是{iter[14]}")
                        goal_Sum = goal_Sum + iter[14]
                        break
            print(f"{goal_Sum / GT_num}是{j}同学的总分")
            sql = f"INSERT INTO zip VALUES({random.randint(0, 99999999)},{j},{goal_Sum / GT_num})"
            cursor.execute(sql)
            cursor.connection.commit()
            # zip表制作完成
        sql = f"SELECT * FROM zip ORDER BY Dice_Average DESC;"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
        student_scores = {}
        for iter in result:
            if iter[1] not in student_scores or iter[2] > student_scores[iter[1]]:
                student_scores[iter[1]] = iter[2]
        print(student_scores)
        # for student_id, highest_goal in student_scores.items():
        #     print(f"Student ID: {student_id}, Highest Goal: {highest_goal}")
        return render_template("/rankrankrank.html", rank=student_scores)


# 开始运行
if __name__ == '__main__':
    # app.run()
    server = pywsgi.WSGIServer(('0.0.0.0', 6006), app)
    server.serve_forever()
