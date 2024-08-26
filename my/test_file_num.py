import os

# 统计文件中是否包含1类别，统计文件中0字节的文件
from extract.utils.file import Walk


def count_file_class_num(file_path):
    file_list = Walk(file_path, ["txt"])
    size_0 = 0
    dict_class_num = {}
    for file_name in file_list:
        with open(file_name) as f:
            size = os.path.getsize(file_name)
            if size == 0:
                size_0 += 0
                continue
            for line in f:
                cla = line.strip().split(" ")[0]
                if cla in dict_class_num:
                    dict_class_num[cla] += 1
                else:
                    dict_class_num[cla] = 1
    dict_class_num["size_0"] = size_0
    print(dict_class_num)

def update_txt_class(path):
    file_list = Walk(path,["txt"])
    for file in file_list:
        file_write_data = []
        with open(file) as f:
            for line in f:
                line = line.strip().split(" ")
                if line[0] == "1":
                    line[0] = "0"
                    file_write_data.append(" ".join(line)+"\n")

        with open(file,"a") as fw:
            fw.write()
        print(f"文件写入完成：{file}")




if __name__ == '__main__':
    count_file_class_num("/media/xin/data1/data/dirty_data/ALL/labels/TRAIN/20240228_shunyi_dirty_liquid_solid")
    count_file_class_num("/media/xin/data1/data/dirty_data/ALL/labels/TRAIN/20240228_shunyi_dirty")
    # print(update_txt_class("/media/xin/data1/data/0228_1"))