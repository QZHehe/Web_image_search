import os
import numpy as np
from skimage.io import imread, imsave
from skimage.color import rgb2lab, lab2rgb
from sklearn.metrics import euclidean_distances
# root = os.path.dirname(__file__)
# file_name = os.path.join(root, 'show_image.png')
# tfname = file_name
# img=imread('./static/Uploads/test1.jpg')
# imsave('hello.png',img)
dui=open('test.png', 'rb').read().encode('base64')
file2=dui.decode('base64')
leniyimg = open('imgout.png','wb')
leniyimg.write(file2)
leniyimg.close()
i=0;