import scipy
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import io

class DataLoader():
    def __init__(self, validation_file, train_file, img_res=(128, 128)):
        self.validation_file = validation_file
        self.train_file = train_file
        self.img_res = img_res

        self.validation_lines = read_lines(self.validation_file)
        self.train_lines = read_lines(self.train_file)
        #print('Train:', len(self.train_lines), 'Validation:', len(self.validation_lines))

    def load_data(self, batch_size=1, is_testing=False):
        batch = self.train_lines if not is_testing else self.validation_lines
        np.random.shuffle(batch)
        batch_images = batch

        imgs_A = []
        imgs_B = []
        i=0
        for img_paths in batch_images:
            if i == batch_size:
                break
            i+=1
            img_A, img_B = self.read_images(img_paths)

            img_A = scipy.misc.imresize(img_A, self.img_res)
            img_B = scipy.misc.imresize(img_B, self.img_res)

            # If training => do random flip
            if not is_testing and np.random.random() < 0.5:
                img_A = np.fliplr(img_A)
                img_B = np.fliplr(img_B)

            imgs_A.append(img_A)
            imgs_B.append(img_B)

        imgs_A = np.array(imgs_A)/127.5 - 1.
        imgs_B = np.array(imgs_B)/127.5 - 1.

        return imgs_A, imgs_B

    def load_batch(self, batch_size=1, is_testing=False):
        batch_images = self.train_lines if not is_testing else self.validation_lines
        np.random.shuffle(batch_images)
        n_batches = int(len(batch_images) / batch_size)

        if(is_testing):
            self.n_val_batches = n_batches
        else:
            self.n_batches = n_batches

        print('BatchSize{1}: Batches: {0}'.format(n_batches, batch_size), flush=True)

        for i in range(n_batches-1):
            batch = batch_images[i*batch_size:(i+1)*batch_size]
            imgs_A, imgs_B = [], []
            for imgs in batch:
                img_A, img_B = self.read_images(imgs)

                img_A = scipy.misc.imresize(img_A, self.img_res)
                img_B = scipy.misc.imresize(img_B, self.img_res)

                if not is_testing and np.random.random() > 0.5:
                        img_A = np.fliplr(img_A)
                        img_B = np.fliplr(img_B)

                imgs_A.append(img_A)
                imgs_B.append(img_B)

            imgs_A = np.array(imgs_A)/127.5 - 1.
            imgs_B = np.array(imgs_B)/127.5 - 1.

            yield imgs_A, imgs_B

    def convert(self, image):
        image = np.array(image, dtype='float32')
        image = scipy.misc.imresize(image, self.img_res)
        images = [image]
        images = np.array(images)/127.5 - 1.
        return images

    def read_images(self, line):
        pathA, pathB = line.split(' ')
        return self.imread(pathB), self.imread(pathA)

    def imread(self, path):
        return scipy.misc.imread(path, mode='RGB').astype(np.float)

def read_lines(file_path):
    if file_path is None: return []

    lines = []
    with open(file_path,'r') as file:
        lines = file.readlines()
    
    lines = [line.replace('\n','').replace('\\','/') for line in lines]
    return lines