import cv2
import numpy as np

# 读取四张图像
img1 = cv2.imread("/home/xin/Desktop/img/04_1614045300920498.jpg")
img2 = cv2.imread("/home/xin/Desktop/img/04_1614045300920498.png")
img3 = cv2.imread("/home/xin/Desktop/img/112.png")
img4 = cv2.imread("/home/xin/Desktop/img/desktopview_04_1614045300920498.png")

# 将前三张图像纵向拼接起来
h1, w1 = img1.shape[:2]
h2, w2 = img2.shape[:2]
h3, w3 = img3.shape[:2]
max_width = max(w1, w2, w3)

result_top = np.zeros((h1+h2+h3, max_width, 3), dtype=np.uint8)
result_top[0:h1, 0:w1] = img1
result_top[h1:h1+h2, 0:w2] = img2
result_top[h1+h2:h1+h2+h3, 0:w3] = img3

# 调整 result_top 的大小，使其与 result 的大小相匹配
h4, w4 = img4.shape[:2]
max_height = max(h1, h2, h3, h4)

result_top_resized = cv2.resize(result_top, (max_width, max_height))

# 将拼接后的图像与第四张图像横向拼接
result = np.zeros((max_height, max_width+w4, 3), dtype=np.uint8)
result[0:max_height, 0:max_width] = result_top_resized
result[0:h4, max_width:max_width+w4] = img4



# 显示结果
cv2.imwrite("/home/xin/Desktop/img/result.png",result)
cv2.imshow("Result", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
