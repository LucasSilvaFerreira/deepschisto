__author__ = 'lucas'
# -*- coding: utf-8 -*-
import sys
from skimage import io, transform, filters, feature, measure
from scipy import mean
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from glob import glob
import re
import os
from tqdm import tqdm

def img_mean(img_array):
    return mean([y for x in img_array for y in x])

class PairsImgsException(Exception):

        def __init__(self, file_name):
            sys.stderr.write('\nFile: {} NOT FOUND\n'
                             'The processing needs 2 files (your_img_name.png (original img) and pontos_you_img_name.png(original with/ red dots inside cells)) for each image \n'.format(file_name))
            sys.exit()


class image_data():

    def __init__(self, path_for_img, filter_gray=0.00001):
        self.img = self.__open_image(path_for_img, filter_gray)





    def __open_image(self, img_path, filter_g):
        img_open = io.imread(img_path,as_grey=True)
        print img_open.shape
        if filter_g != 0.00001:
            img_open[img_open > filter_g] = 1
        return transform.resize(img_open, (800, 800))



    def sliding_window(self, stepSize, windowSize, rotate=False):

        if rotate:
            image = self.rotate_img()
        else:
            image = self.img
        # slide a window across the image

        for y in xrange(0, image.shape[0], stepSize):

            for x in xrange(0, image.shape[1], stepSize):

                # yield the current window


                yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

    def show(self):
        io.imshow(self.img)
        io.show()


    def rotate_img(self):
        return transform.rotate(self.img, 90, resize=True)


class generate_sliced_imgs():

    def __init__(self, img_dir_path):
        self.imgs_path = img_dir_path
        self.pairs_img = self.parse_imgs()
        self.slice_imgs()


    def parse_imgs(self):
        files = glob(self.imgs_path+'//*png'.replace("//", '/'))
        pairs_all = [[f, f.replace(f.split('/')[-1], 'pontos_'+ f.split('/')[-1] )] for f in files if not re.search('pontos_', f) ]
        for p in pairs_all: # testing files
            for p_f in p:
                if not os.path.exists(p_f):
                    PairsImgsException(p_f)

        return pairs_all

    def slice_imgs(self):
        for pair in tqdm(self.pairs_img):

            for rotate in [False, True]:

                img1 = image_data(pair[1], filter_gray=0.25)
                full = image_data(pair[0])
                file_name = pair[0].split('/')[-1].split('.')[0]

                print 'slicing: {}'.format(file_name)
                window_size = 35 * 4

                for slice_img, original_slice in zip(img1.sliding_window(12 * 4, [window_size, window_size],rotate=rotate ),
                                                     full.sliding_window(12 * 4, [35 * 4, 35 * 4], rotate=rotate) ):

                    mean_img = img_mean(slice_img[2])

                    if mean_img < 1:
                        img_label = measure.label(slice_img[2])
                        count = 0
                        for region in measure.regionprops(img_label):
                            if region.area > 40 and region.area < 150:
                                count += 1
                        print count

                        if slice_img[2].shape == (window_size, window_size):
                            io.imsave(
                                fname='/home/lucas/PycharmProjects/deepschisto/sliced_figures/{}_cellcount={}.png'.format(
                                    '_'.join(map(str, [file_name, 'rotate=', rotate, slice_img[0], slice_img[1]])), str(count)),
                                arr=original_slice[2]
                                )
                        else:
                            print 'size expected: {} size found: {}'.format((window_size, window_size), slice_img[2].shape )


                # print 'shape', img1.img.shape
                # for region in measure.regionprops(img_label):
                #     if region.area > 50 and region.area < 150:
                #         padding = 25
                #         minr, minc, maxr, maxc = region.bbox
                #         print minr, minc, maxr, maxc
                #
                #         if minr > padding and (maxr + padding) < img1.img.shape[0] and minc > padding and (maxc + padding) < \
                #                 img1.img.shape[1]:
                #             minr = minr - padding
                #             minc = minc - padding
                #             maxr = maxr + padding
                #             maxc = maxc + padding
                #
                #             io.imshow(full.img[minr:maxr, minc:maxc])
                #             io.show()
                #
                #
                #             # rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                #             #                           fill=False, edgecolor='red', linewidth=2)
                #             #
                #             #
                #             #
                #             # ax.add_patch(rect)







def main():
    obj_gene = generate_sliced_imgs("/home/lucas/PycharmProjects/deepschisto/figuras")
    exit()
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))



    img1 = image_data('/home/lucas/PycharmProjects/deepschisto/vermelho_teste.png', filter_gray=0.25)
    full = image_data('/home/lucas/PycharmProjects/deepschisto/foto_teste.png')

    #ax.imshow(img1.img)


    for slice_img, original_slice in zip(img1.sliding_window(12*4, [35*4, 35*4]), full.sliding_window(12*4, [35*4, 35*4]) ):
        mean_img = img_mean(slice_img[2])

        if mean_img < 1:
            # io.imshow(original_slice[2])
            # io.show()


            img_label = measure.label(slice_img[2])

            count = 0
            for region in measure.regionprops(img_label):
                if region.area > 40 and region.area < 150:
                    count +=1
            print count

            if count > 0:
                io.imsave(fname = '/home/lucas/PycharmProjects/deepschisto/slice_figures/{}_cellcount={}.png'.format('_'.join(map(str, [slice_img[0], slice_img[1]])),str(count)),
                          arr=original_slice[2]
                          )
            else:
                print 'It didnt find cells'




    print 'shape', img1.img.shape
    for region in measure.regionprops(img_label):
        if region.area > 50 and region.area < 150:
            padding = 25
            minr, minc, maxr, maxc = region.bbox
            print minr, minc, maxr, maxc

            if minr > padding and (maxr + padding) < img1.img.shape[0] and minc > padding and (maxc + padding) < img1.img.shape[1]:

                minr = minr - padding
                minc = minc - padding
                maxr = maxr + padding
                maxc = maxc + padding

                io.imshow(full.img[minr:maxr, minc:maxc])
                io.show()


                # rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                #                           fill=False, edgecolor='red', linewidth=2)
                #
                #
                #
                # ax.add_patch(rect)

    print len(img_label)
    plt.show()



if __name__ == '__main__':
    sys.exit(main())
