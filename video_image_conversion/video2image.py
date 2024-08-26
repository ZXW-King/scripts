import cv2
import os
import numpy as np

def rotate_image(image, angle,iscrop=False):
    """
    旋转图像。

    参数：
    image (ndarray): 输入图像。
    angle (float): 旋转角度。

    返回值：
    ndarray: 旋转后的图像。
    """
    # 获取图像尺寸
    (h, w) = image.shape[:2]
    # 计算图像中心
    center = (w / 2, h / 2)

    # 计算旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 计算旋转后的新边界框
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # 调整旋转矩阵以考虑平移
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # 执行实际的旋转并返回图像
    rotated = cv2.warpAffine(image, M, (new_w, new_h))
    if iscrop:
        height,width = rotated.shape[:2]
        # 定义左右裁剪的边界
        left_crop = 400
        right_crop = width - 400
        # 进行裁剪
        img_cropped = rotated[:, left_crop:right_crop, :]
        return img_cropped
    else:
        return rotated


def video_to_images(video_path, output_dir, step_frame=1,frame_prefix='frame', img_format='jpg',rotate_angle=0):
    """
    将视频拆分成单独的图像并保存到指定目录。

    参数：
    video_path (str): 视频文件的路径。
    output_dir (str): 保存图像的目录路径。
    frame_prefix (str): 图像文件名前缀，默认值为 'frame'。
    img_format (str): 图像文件格式，默认值为 'jpg'。
    """

    # 创建保存图像的目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 检查视频是否成功打开
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    else:
        fps = cap.get(cv2.CAP_PROP_FPS)  # 帧率，视频每秒展示多少张图片
        print('fps:', fps)

    frame_count = 1 # 用于统计所有帧数
    count = 0
    # 逐帧读取视频
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Process finished!")
            break
        else:
            if frame_count % step_frame == 0:
                # 如果需要旋转图像
                if rotate_angle != 0:
                    frame = rotate_image(frame, rotate_angle)
                # 构造输出图像的文件名
                img_name = f"{frame_prefix}_{count:04d}.{img_format}"
                img_path = os.path.join(output_dir, img_name)

                # 保存图像
                cv2.imwrite(img_path, frame)
                count += 1

        frame_count += 1

    # 释放视频捕获对象
    cap.release()

    print(f"Total frames extracted: {frame_count}")
    print("Done!")

if __name__ == '__main__':
    # 示例使用
    # video_path = '/media/xin/data/data/face_data/test_data/FairPhone5广角采集预览录屏/室内灯光/0.8m-三人screen-20240417-102457.mp4'
    video_path = '/media/xin/data/data/face_data/indemind_data/IOS_18608_1718360662.mp4'
    output_dir = video_path.split(".")[0]
    if not os.path.exists(os.path.dirname(output_dir)):
        os.makedirs(os.path.dirname(output_dir))
    video_to_images(video_path, output_dir,rotate_angle=0)

