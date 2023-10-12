import tensorflow as tf
from tensorflow import keras
import cv2
import numpy as np

# 加载预训练的超分辨率模型，这里使用的是SRCNN
model = keras.models.load_model('super_resolution_model.h5')

# 读取输入图像
input_image_path = 'input_image.jpg'
output_image_path = 'output_image.jpg'
input_image = cv2.imread(input_image_path)

# 将输入图像缩放到模型所需的大小
input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2YCrCb)  # 转换为YCrCb颜色空间
input_image = cv2.resize(input_image, (model.input_shape[1], model.input_shape[2]))
input_image = input_image / 255.0  # 归一化像素值

# 使用模型进行超分辨率处理
output_image = model.predict(np.expand_dims(input_image, axis=0))[0]

# 将输出图像反向变换到BGR颜色空间
output_image *= 255.0
output_image = np.clip(output_image, 0, 255)
output_image = cv2.cvtColor(output_image.astype(np.uint8), cv2.COLOR_YCrCb2BGR)

# 保存超分辨率处理后的图像
cv2.imwrite(output_image_path, output_image)

print("超分辨率处理完成，结果已保存至", output_image_path)
