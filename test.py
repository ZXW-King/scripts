"""
测试图像生成的数量以及相差的图像
"""
import os
i = 2
path = f"/media/xin/data1/data/parker_data/2022_08_22/louti/data_2023_0822_{i}"
path2 = f"/media/xin/data1/data/parker_data/tof_label/louti/data_2023_0822_{i}/result_image_with_tof"
path3 = f"/media/xin/data1/data/parker_data/tof_label/louti/data_2023_0822_{i}/result_tof"

l2 = []
for pi in os.listdir(path2):
    pi = pi.replace("png","jpg")
    l2.append(pi)

l3 = []
for tof in os.listdir(path3):
    pi = tof.replace("png","jpg")
    l3.append(pi)

l1 = []
for p in os.listdir(path):
    p_path = os.path.join(path,p)
    if os.path.isdir(p_path):
        cam0 = os.path.join(p_path,'cam0')
        for o in os.listdir(cam0):
            l1.append(o)
            if o not in l2:
                print(os.path.join(cam0,o))
print("原数据：",len(l1))
print("image with tof",len(l2))
print("only tof",len(l3))