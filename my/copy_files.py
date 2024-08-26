import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 定义源目录和目标目录
source_dir = "/media/xin/data/data/disk_data/datasets.epfl.ch/disk-data/megadepth/scenes"
destination_dir = "/media/xin/Seagate Basic/公司资料/INDEMIND/data/disk-data/megadepth/scenes"

# 如果目标目录不存在，创建它
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# 获取源目录中的所有文件和文件夹
items = os.listdir(source_dir)


# 定义拷贝函数
def copy_item(item):
    source_path = os.path.join(source_dir, item)
    destination_path = os.path.join(destination_dir, item)

    # 使用 cp 命令拷贝文件或文件夹
    subprocess.run(["cp", "-r", source_path, destination_path], check=True)

    return item


# 使用 ThreadPoolExecutor 实现多线程拷贝
with ThreadPoolExecutor(max_workers=4) as executor:  # max_workers 可根据需要调整
    # 提交所有拷贝任务，并在完成时使用 tqdm 显示进度
    futures = {executor.submit(copy_item, item): item for item in items}

    for future in tqdm(as_completed(futures), total=len(futures), desc="Copying files", unit="file"):
        item = futures[future]
        try:
            future.result()
            print(f"Copied: {item}")
        except Exception as e:
            print(f"Failed to copy {item}: {e}")

print("Copy completed!")
