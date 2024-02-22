import os
import shutil

def cp_label_desk():
    txt_path = '/media/xin/data1/data/parker_data/result/label/result.txt'
    with open(txt_path,"r") as f:
        for line in f:
            path = line.strip()
            path1 = path.replace('label','2022_08_22_remap')
            dirname = os.path.dirname(path1)
            image_name = os.path.basename(path1).replace('.xml','.jpg')
            cam0_path = os.path.join(dirname,'cam0')
            cam1_path = os.path.join(dirname,'cam1')

            path_cam0_image = os.path.join(cam0_path,image_name)
            path_cam1_image = os.path.join(cam1_path,image_name)
            # /media/xin/data1/data/parker_data/result/img_tree
            path_cam0_image_new = path_cam0_image.replace('2022_08_22_remap','result/img_tree')
            path_cam1_image_new = path_cam1_image.replace('2022_08_22_remap','result/img_tree')
            dirname_cam0 = os.path.dirname(path_cam0_image_new)
            dirname_cam1 = os.path.dirname(path_cam1_image_new)
            if not os.path.exists(dirname_cam0):
                os.makedirs(dirname_cam0)
            if not os.path.exists(dirname_cam1):
                os.makedirs(dirname_cam1)
            shutil.copyfile(path_cam0_image, path_cam0_image_new)
            shutil.copyfile(path_cam1_image, path_cam1_image_new)
            print(f"{image_name}完成拷贝！")


def cp_tof_label_desk(path):
    for i in range(3):
        path1 = "data_2023_0822_" + str(i)
        dir_path1 = os.path.join(path,path1)
        tof = f'/media/xin/data1/data/parker_data/tof_label/da/{path1}/result_tof'
        tof_list = os.listdir(tof)
        for l in os.listdir(dir_path1):
            cam0 = os.path.join(dir_path1,l)
            cam0_path = cam0+"/cam0"  # '/media/xin/data1/data/parker_data/result/img_tree/louti/data_2023_0822_0/20210223_1346/cam0'
            save_label_path = os.path.join('/media/xin/data1/data/parker_data/result/tof_label',"/".join(cam0_path.split("/")[-4:]))
            if not os.path.exists(save_label_path):
                os.makedirs(save_label_path)
            for img in os.listdir(cam0_path):
                img_name = img.replace('.jpg','.png')
                if img_name in tof_list:
                    path_cam0_image_label = os.path.join(tof,img_name)
                    path_cam0_image_label_new = os.path.join(save_label_path,img_name)
                    shutil.copyfile(path_cam0_image_label, path_cam0_image_label_new)
                    print(img_name+":完成")


def diff_txt(txt1,txt2):
    l1 = []
    l2 = []
    with open(txt1,'r') as f:
        for l in f:
            l1.append(l.strip())
    with open(txt2,'r') as f2:
        for line in f2:
            line = line.strip()
            l2.append(line)
            if line not in l1:
                print(line)
    print(len(l1))
    print(len(l2))

def choose_desk_txt(img_path,txt_path):
    imgs_path = os.listdir(img_path)
    save_txt_path = txt_path.replace("sync.txt","with_desk.txt")
    write_file = open(save_txt_path,"w")
    for i in imgs_path:
        cam0 = os.path.join(img_path,i+"/cam0")
        with_desk_img = os.listdir(cam0)
        with open(txt_path) as f:
            for line in f:
                img = line.strip().split(' ')[0].split("/")[-1]
                if img in with_desk_img:
                    write_file.write(line)
                    write_file.flush()
    write_file.close()





if __name__ == '__main__':
    # P = "/media/xin/data1/data/parker_data/result/img_tree/da"
    # cp_tof_label_desk(P)

    # txt1 = '/media/xin/data1/data/parker_data/result/image_list.txt'
    # txt2 = '/media/xin/data1/data/parker_data/result/image_names_label.txt'
    # diff_txt(txt2,txt1)

    txtpath = "/media/xin/data1/data/parker_data/2022_08_22/louti/data_2023_0822_0/sync.txt"
    choose_desk_txt("/media/xin/data1/data/parker_data/result/img_tree/louti/data_2023_0822_0",txtpath)