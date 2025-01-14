import os
import glob
import numpy as np
import albumentations
from torch.utils.data import Dataset

from taming.data.base import ImagePaths, NumpyPaths, ConcatDatasetWithIndex


class ObjectsBase(Dataset):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.data = None
        self.keys = None

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        example = self.data[i]
        ex = {}
        if self.keys is not None:
            for k in self.keys:
                ex[k] = example[k]
        else:
            ex = example
        return ex


class ShapeNetTrain(ObjectsBase):
    def __init__(self, size, keys=None):
        super().__init__()
        root = "data/shapenet"
        with open("data/shapenet/train.txt", "r") as f:
            relpaths = f.read().splitlines()
        paths = [os.path.join(root, relpath) for relpath in relpaths]
        img_paths = []
        for path in paths:
            all_images = [os.path.join(path, 'r_' + str(i).zfill(2) + '.png') for i in range(24)]
            img_paths.extend(all_images)
        self.data = ImagePaths(paths=img_paths, size=size, random_crop=False)
        self.keys = keys


class ShapeNetValidation(ObjectsBase):
    def __init__(self, size, keys=None):
        super().__init__()
        root = "data/shapenet"
        with open("data/shapenet/val.txt", "r") as f:
            relpaths = f.read().splitlines()
        paths = [os.path.join(root, relpath) for relpath in relpaths]
        img_paths = []
        for path in paths:
            all_images = [os.path.join(path, 'r_' + str(i).zfill(2) + '.png') for i in range(24)]
            img_paths.extend(all_images)
        self.data = ImagePaths(paths=img_paths, size=size, random_crop=False)
        self.keys = keys


class AmazonTrain(ObjectsBase):
    def __init__(self, size, keys=None):
        super().__init__()
        root = "data/amazon"
        with open("data/amazon/train.txt", "r") as f:
            relpaths = f.read().splitlines()
        paths = [os.path.join(root, relpath) for relpath in relpaths]
        img_paths = []
        for path in paths:
            all_images = sorted(glob.glob(os.path.join(path, '*')))
            img_paths.extend(all_images)
        self.data = ImagePaths(paths=img_paths, size=size, random_crop=False)
        self.keys = keys


class AmazonValidation(ObjectsBase):
    def __init__(self, size, keys=None):
        super().__init__()
        root = "data/amazon"
        with open("data/amazon/val.txt", "r") as f:
            relpaths = f.read().splitlines()
        paths = [os.path.join(root, relpath) for relpath in relpaths]
        img_paths = []
        for path in paths:
            all_images = sorted(glob.glob(os.path.join(path, '*')))
            img_paths.extend(all_images)
        self.data = ImagePaths(paths=img_paths, size=size, random_crop=False)
        self.keys = keys


class ObjectsTrain(Dataset):
    def __init__(self, size, keys=None, crop_size=None, coord=False):
        # self.data = ShapeNetTrain(size=size, keys=keys)
        self.data = AmazonTrain(size=size, keys=keys)
        self.coord = coord
        if crop_size is not None:
            self.cropper = albumentations.RandomCrop(height=crop_size,width=crop_size)
            if self.coord:
                self.cropper = albumentations.Compose([self.cropper],
                                                      additional_targets={"coord": "image"})

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        ex = self.data[i]
        if hasattr(self, "cropper"):
            if not self.coord:
                out = self.cropper(image=ex["image"])
                ex["image"] = out["image"]
            else:
                h,w,_ = ex["image"].shape
                coord = np.arange(h*w).reshape(h,w,1)/(h*w)
                out = self.cropper(image=ex["image"], coord=coord)
                ex["image"] = out["image"]
                ex["coord"] = out["coord"]
        # ex["class"] = y # could derive from filepath if needed..
        return ex


class ObjectsValidation(Dataset):
    def __init__(self, size, keys=None, crop_size=None, coord=False):
        # self.data = ShapeNetValidation(size=size, keys=keys)
        self.data = AmazonValidation(size=size, keys=keys)
        self.coord = coord
        if crop_size is not None:
            self.cropper = albumentations.CenterCrop(height=crop_size,width=crop_size)
            if self.coord:
                self.cropper = albumentations.Compose([self.cropper],
                                                      additional_targets={"coord": "image"})

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        ex = self.data[i]
        if hasattr(self, "cropper"):
            if not self.coord:
                out = self.cropper(image=ex["image"])
                ex["image"] = out["image"]
            else:
                h,w,_ = ex["image"].shape
                coord = np.arange(h*w).reshape(h,w,1)/(h*w)
                out = self.cropper(image=ex["image"], coord=coord)
                ex["image"] = out["image"]
                ex["coord"] = out["coord"]
        # ex["class"] = y
        return ex

'''
class FFHQTrain(ObjectsBase):
    def __init__(self, size, keys=None):
        super().__init__()
        root = "data/ffhq"
        with open("data/ffhqtrain.txt", "r") as f:
            relpaths = f.read().splitlines()

        paths = [os.path.join(root, relpath) for relpath in relpaths]
        self.data = ImagePaths(paths=paths, size=size, random_crop=False)
        self.keys = keys


class FFHQValidation(ObjectsBase):
    def __init__(self, size, keys=None):
        super().__init__()
        root = "data/ffhq"
        with open("data/ffhqvalidation.txt", "r") as f:
            relpaths = f.read().splitlines()
        paths = [os.path.join(root, relpath) for relpath in relpaths]
        self.data = ImagePaths(paths=paths, size=size, random_crop=False)
        self.keys = keys


class FacesHQTrain(Dataset):
    # CelebAHQ [0] + FFHQ [1]
    def __init__(self, size, keys=None, crop_size=None, coord=False):
        d1 = CelebAHQTrain(size=size, keys=keys)
        d2 = FFHQTrain(size=size, keys=keys)
        self.data = ConcatDatasetWithIndex([d1, d2])
        self.coord = coord
        if crop_size is not None:
            self.cropper = albumentations.RandomCrop(height=crop_size,width=crop_size)
            if self.coord:
                self.cropper = albumentations.Compose([self.cropper],
                                                      additional_targets={"coord": "image"})

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        ex, y = self.data[i]
        if hasattr(self, "cropper"):
            if not self.coord:
                out = self.cropper(image=ex["image"])
                ex["image"] = out["image"]
            else:
                h,w,_ = ex["image"].shape
                coord = np.arange(h*w).reshape(h,w,1)/(h*w)
                out = self.cropper(image=ex["image"], coord=coord)
                ex["image"] = out["image"]
                ex["coord"] = out["coord"]
        ex["class"] = y
        return ex


class FacesHQValidation(Dataset):
    # CelebAHQ [0] + FFHQ [1]
    def __init__(self, size, keys=None, crop_size=None, coord=False):
        d1 = CelebAHQValidation(size=size, keys=keys)
        d2 = FFHQValidation(size=size, keys=keys)
        self.data = ConcatDatasetWithIndex([d1, d2])
        self.coord = coord
        if crop_size is not None:
            self.cropper = albumentations.CenterCrop(height=crop_size,width=crop_size)
            if self.coord:
                self.cropper = albumentations.Compose([self.cropper],
                                                      additional_targets={"coord": "image"})

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        ex, y = self.data[i]
        if hasattr(self, "cropper"):
            if not self.coord:
                out = self.cropper(image=ex["image"])
                ex["image"] = out["image"]
            else:
                h,w,_ = ex["image"].shape
                coord = np.arange(h*w).reshape(h,w,1)/(h*w)
                out = self.cropper(image=ex["image"], coord=coord)
                ex["image"] = out["image"]
                ex["coord"] = out["coord"]
        ex["class"] = y
        return ex
'''

