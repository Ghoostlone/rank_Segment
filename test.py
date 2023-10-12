import SimpleITK as sitk
import numpy as np

# 读取输入的.nii.gz文件
input_file_path = './static/0f593c1e-4bb8-470f-a87b-fee3dbd3b3ed_0000.nii.gz'
output_path = './static/segmented_output/'
output_file_name = ['0.nii.gz','1.nii.gz', '2.nii.gz', '3.nii.gz','4.nii.gz','5.nii.gz','6.nii.gz','7.nii.gz','8.nii.gz','9.nii.gz','10.nii.gz','11.nii.gz',]

image = sitk.ReadImage(input_file_path)

for i in range(1,12):
    # 创建一个二值图像，只保留值为i的体素
    binary_image = sitk.BinaryThreshold(image, lowerThreshold=i, upperThreshold=i)

    # 将二值图像保存为.nii.gz文件
    sitk.WriteImage(binary_image, output_path+output_file_name[i])

print("分割后的图像已保存。")



def compute_dice_coefficient(label1, label2):
    intersection = np.logical_and(label1, label2)

    dice_coefficient = (2.0 * np.sum(intersection)) / (np.sum(label1) + np.sum(label2))
    return dice_coefficient


# Load the images using SimpleITK
image_X = sitk.ReadImage('./static/0f593c1e-4bb8-470f-a87b-fee3dbd3b3ed_0000.nii.gz')
image_Y = sitk.ReadImage('./static/0f593c1e-4bb8-470f-a87b-fee3dbd3b3ed_0000.nii.gz')

# Convert SimpleITK images to numpy arrays
data_X = sitk.GetArrayFromImage(image_X)
data_Y = sitk.GetArrayFromImage(image_Y)

# Assuming the labels you want to compare are binary masks
label_X = data_X > 0
label_Y = data_Y > 0

dice_coefficient = compute_dice_coefficient(label_X, label_Y)
print(f"Dice Coefficient: {dice_coefficient:.4f}")

