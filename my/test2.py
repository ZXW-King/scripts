"判断文件大小为0的个数"
import os.path
import pandas as pd
import numpy as np

def read_txt(txt_file):
    df = pd.read_csv(txt_file,delim_whitespace=True,header=None)
    data = int(df.values[0][0].item())
    return str(data)


def get_file_count(file_names_list,file_path):
    file_name_dict = {}
    class_name_dict = {}
    no_count_0 = 0
    count_0 = 0
    data_list = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            for file_name in file_names_list:
                if file_name in os.path.split(line)[0].split("/"):
                    if file_name in file_name_dict:
                        file_name_dict[file_name] +=1
                    else:
                        file_name_dict[file_name] = 1
            line = line.replace("JPEGImages","labels")
            if "jpg" in line:
                line = line.replace("jpg","txt")
            elif "png" in line:
                line = line.replace("png", "txt")
            size = os.path.getsize(line)
            if size == 0:
                count_0 += 1
            else:
                no_count_0 += 1
                data = read_txt(line)
                if data in class_name_dict:
                    class_name_dict[data] += 1
                else:
                    class_name_dict[data] = 1
    print(class_name_dict)
    print(f"负样本数据集为:{count_0}，非负样本数据集为:{no_count_0},合计为:{count_0+no_count_0}")
    print(file_name_dict)

# print(get_file_count("/media/xin/data1/data/dirty_data/ALL/darknet/version3.0.0/train.txt"))
file_path = "/media/xin/data1/data/dirty_data/ALL/JPEGImages/TRAIN"
file_names = os.listdir(file_path)
get_file_count(file_names,"/media/xin/data1/data/dirty_data/ALL/darknet/version10.0.8/val.txt")

