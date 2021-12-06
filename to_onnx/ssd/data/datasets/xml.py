import os
import torch.utils.data
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image
from to_onnx.ssd.structures.container import Container
import sys
import abc
from .utils.utils import Empty
from .utils.xml import WriteXML
import cv2
from random import randint, choice, uniform
from .utils.image_process import have_color, transparent, augment, to_transparent, Gray
from to_onnx.ssd.utils.utils import Walk

class XML(torch.utils.data.Dataset):
    __metaclass__ = abc.ABCMeta
    class_names = []

    def __init__(self, data_dir, image_sets_file, target, transform=None, target_transform=None, keep_difficult=False, train=False):
        self.data_dir = data_dir
        self.transform = transform
        self.target_transform = target_transform
        self.file_list = XML._read_image_ids(image_sets_file)
        self.keep_difficult = keep_difficult
        self.class_dict = {class_name: i for i, class_name in enumerate(self.class_names)}
        self.ignore = []
        self.train = train
        self._init_targets(target)

    def concate(self, xml):

        '''
        temp strategy: make sure they have:
                - same date_dir
                - same class name/number
        '''
        assert  isinstance(xml, XML)
        self.file_list.extend(xml.file_list)


    def _init_targets(self, path):
        self.with_mixup = False
        self.target_scale = (40, 90)
        self.target = None

        if None == path or '' == path or not self.train:
            self.with_mixup = False
            return

        self.with_mixup = True

        print("loading targets...")
        file_list = Walk(path, ['jpg', 'png'])
        target_length = len(path)
        self.target = dict()

        for file in file_list:
            name = file[target_length+1:].split('/')[0]
            if name not in self.class_names:
                continue
            image = cv2.imread(file, cv2.IMREAD_UNCHANGED)
            h, w, c = image.shape
            if w < 20 or h < 20:
                continue

            image = to_transparent(image)

            if name in self.target:
                self.target[name].append(image)
            else:
                self.target[name] = [image,]
        return self

    def _ann_file(self, image_id):
        return os.path.join(self.data_dir, os.path.splitext(image_id)[0] + ".xml")

    def _next(self, index):
        return (index+1) % len(self.file_list)

    def _raiseNofile(self, index):
        raise IOError("no such file: ", self.get_file(index)[0])

    def _randomTarget(self, color):
        class_name = choice(list(self.target))
        img_id = randint(0, len(self.target[class_name])-1)
        target = self.target[class_name][img_id]

        if not color:
            target = Gray(target)

        return target, self.class_dict[class_name]

    def _gen_foreground(self, img):
        mask_all = np.full_like(img, 255)
        target_all = np.zeros_like(img)
        min_size, max_size = self.target_scale
        h, w, _ = mask_all.shape
        num_w, num_h = w // max_size, h // max_size
        boxes, labels = [], []

        for i in range(num_w):
            for j in range(0, num_h):
                if not (0==i and num_h-1==j) and uniform(0, 1) > 0.5:
                    continue

                target, target_name = self._randomTarget(color=have_color(img))
                target = augment(target, 0, 0)

                # random resize
                size = randint(min_size, max_size)
                x1, y1 = randint(i*max_size, (i+1) * max_size - size), randint(j*max_size, (j+1) * max_size - size)
                x2, y2 = x1+size, y1+size
                target = cv2.resize(target, (size, size))

                # prepare for mixup: img,  mask
                if transparent(target):
                    mask = target[:, :, 3]
                    mask = np.tile(mask[:, :, np.newaxis], (1, 1, 3))
                    target = cv2.bitwise_and(target[:, :, 0:3], mask)
                    mask_all[y1:y2, x1:x2, :] = cv2.bitwise_not(mask)
                else:
                    mask_all[y1:y2, x1:x2, :] = 0

                target_all[y1:y2, x1:x2, :] = target

                boxes.append([x1, y1, x2, y2])
                labels.append(target_name)

        return mask_all, target_all, boxes, labels

    def _mixup(self, img, boxes, labels, erase=True):
        mask_all, target_all, boxes_new, labels_new = self._gen_foreground(img)

        if erase:
            img = cv2.bitwise_and(img, mask_all)
            img = cv2.add(img, target_all)
        else:
            img_obj = cv2.bitwise_and(img, np.full_like(mask_all, 255) - mask_all)
            ratio = uniform(0.7, 1)
            img_obj = cv2.addWeighted(img_obj, 1-ratio, target_all, ratio, 0)
            img_background = cv2.bitwise_and(img, mask_all)
            img = cv2.add(img_background, img_obj)

        if 0 != len(boxes_new):
            boxes_new = np.array(boxes_new, ndmin=2).astype(np.float32) - 1
            labels_new = np.array(labels_new).astype(np.int64)

            boxes = np.concatenate((boxes, boxes_new), axis=0) if len(boxes) != 0 else boxes_new
            labels = np.concatenate((labels, labels_new), axis=0) if len(labels) != 0 else labels_new

        return img, boxes, labels

    def _get_item(self, index):
        image_file, ann_file = self.get_file(index)
        image = self.read_image(image_file)
        boxes, labels = self.get_annotation(ann_file)

        if self.with_mixup and Empty(boxes) and not have_color(image):
            image, boxes, labels = self._mixup(image, boxes, labels)
        if Empty(boxes):
            if have_color(image) or not self.with_mixup:
                return self._get_item(self._next(index))

            if self.train:
                print("no object: ", self.get_file(index)[0])
                sys.exit(0)
            else:
                return self._get_item(self._next(index))

        return image, boxes, labels

    def __getitem__(self, index):
        image, boxes, labels = self._get_item(index)

        if self.transform:
            image, boxes, labels = self.transform(image, boxes, labels)
        if self.target_transform:
            boxes, labels = self.target_transform(boxes, labels)

        targets = Container(boxes=boxes,labels=labels,)
        return image, targets, index

    @abc.abstractmethod
    def get_file(self, index):
        pass

    def __len__(self):
        return len(self.file_list)

    @staticmethod
    def _read_image_ids(image_sets_file):
        ids = []
        with open(image_sets_file) as f:
            for line in f:
                ids.append(line.rstrip())
        return ids

    def get_annotation(self, ann_file):
        if not os.path.exists(ann_file):
            if self.with_mixup:
                return (np.array([]), np.array([]))
            else:
                raise IOError("no such file: ", ann_file)

        objects = ET.parse(ann_file).findall("object")
        boxes = []
        labels = []
        is_difficult = []
        for obj in objects:
            class_name = obj.find('name').text.lower().strip()
            if class_name not in self.class_names:
                continue
            bbox = obj.find('bndbox')
            # VOC dataset format follows Matlab, in which indexes start from 0
            x1 = float(bbox.find('xmin').text) - 1
            y1 = float(bbox.find('ymin').text) - 1
            x2 = float(bbox.find('xmax').text) - 1
            y2 = float(bbox.find('ymax').text) - 1
            boxes.append([x1, y1, x2, y2])
            labels.append(self.class_dict[class_name])
            difficule_flag = obj.find('difficult')
            is_difficult_str = difficule_flag.text if difficule_flag is not None else False
            is_difficult.append(int(is_difficult_str) if is_difficult_str else 0)

        boxes = np.array(boxes, dtype=np.float32)
        labels = np.array(labels, dtype=np.int64)
        is_difficult =  np.array(is_difficult, dtype=np.uint8)
        if not self.keep_difficult:
            boxes = boxes[is_difficult == 0]
            labels = labels[is_difficult == 0]

        return (boxes, labels)

    def save_annotation(self, box_list, label_list, score_list, thresholds, path):
        file_list = [os.path.join(path, os.path.splitext(f)[0] + ".xml") for f in self.file_list]
        for i, (box, label, score, file) in enumerate(zip(box_list, label_list, score_list, file_list)):
            if len(box) == 0:
                continue
            box = box[score > thresholds[label]]
            info = self.get_img_info(i)
            WriteXML(box, label, info['width'], info['height'], file, self.class_names)

    def get_img_info(self, index):
        img_id, annotation_file = self.get_file(index)
        anno = ET.parse(annotation_file).getroot()
        size = anno.find("size")
        im_info = tuple(map(int, (size.find("height").text, size.find("width").text)))
        return {"height": im_info[0], "width": im_info[1]}

    def read_image(self, image_file):
        try:
            image = Image.open(image_file).convert("RGB")
            image = np.array(image)
            return image
        except:
            raise IOError("no such file: ", image_file)
