# -*- coding:utf-8 -*-
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 计算透视变换参数矩阵
def cal_perspective_params(img, points):
    # 设置偏移点。如果设置为(0,0),表示透视结果只显示变换的部分（也就是画框的部分）
    offset_x =130
    offset_y = 320
    img_size = (img.shape[1], img.shape[0])
    src = np.float32(points)

    # 选取四个点，分别是左上、右上、左下、右下
    # 透视变换的四个点
    # dst = np.float32([[offset_x, offset_y], [img_size[0] - offset_x, offset_y],
    #                   [offset_x, img_size[1] - offset_y], [img_size[0] - offset_x, img_size[1] - offset_y]])
    dst = np.float32([[40,20], [600,20],
                      [0,320], [640,320]])

    # 透视矩阵
    M = cv2.getPerspectiveTransform(src, dst)
    print(M)
    # 透视逆矩阵
    M_inverse = cv2.getPerspectiveTransform(dst, src)
    print(M_inverse)
    return M, M_inverse

# 透视变换
def img_perspect_transform(img, M):
    img_size = (img.shape[1], img.shape[0])
    return cv2.warpPerspective(img, M, img_size)

def draw_line(img,p1,p2,p3,p4):
    points = [list(p1), list(p2), list(p3), list(p4)]
    # 画线
    img = cv2.line(img, p1, p2, (0, 0, 255), 3)
    img = cv2.line(img, p2, p4, (0, 0, 255), 3)
    img = cv2.line(img, p4, p3, (0, 0, 255), 3)
    img = cv2.line(img, p3, p1, (0, 0, 255), 3)
    return points,img

if __name__ == '__main__':
    # 观察图像像素大小，便于手动选点
    img = cv2.imread('/data/VOC/ABBY/JPEGImages/TEST/20220419/data-77/gray/cam0/2022_04_02_08_34_39_1648888479855.jpg')
    plt.figure()
    plt.imshow(img)
    plt.show()
    # 选取四个点，分别是左上、右上、左下、右下
    points, img = draw_line(img, (0, 0), (640, 0), (0, 400), (640, 400))
    # cv2.imshow('test01',img)
    # cv2.waitKey(0)
    cv2.imwrite('test01.png',img)
    M, M_inverse = cal_perspective_params(img, points)
    trasform_img = img_perspect_transform(img, M)
    # 观察透视图像像素大小
    plt.figure()
    plt.imshow(trasform_img)
    plt.show()
    # cv2.imshow('test02.png',trasform_img)
    # cv2.waitKey(0)
    cv2.imwrite('test02.png',trasform_img)
