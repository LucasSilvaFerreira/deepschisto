__author__ = 'lucas'
# -*- coding: utf-8 -*-
import sys
from skimage import io, transform, filters, feature, measure
from scipy import mean
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

def img_mean(img_array):
    return mean([y for x in img_array for y in x])

class image_data():

    def __init__(self, path_for_img, filter_gray=0.00001):
        self.img = self.__open_image(path_for_img, filter_gray)





    def __open_image(self, img_path, filter_g):
        img_open = io.imread(img_path,as_grey=True)
        print img_open.shape
        if filter_g != 0.00001:
            img_open[img_open > filter_g] = 1
        return transform.resize(img_open, (800, 800))



    def sliding_window(self, stepSize, windowSize):
        image = self.img
        # slide a window across the image

        for y in xrange(0, image.shape[0], stepSize):

            for x in xrange(0, image.shape[1], stepSize):

                # yield the current window


                yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

    def show(self):
        io.imshow(self.img)
        io.show()


def main():
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
