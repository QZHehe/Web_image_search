import sys
import os
# from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure
# from bson import Binary
# import cPickle
# import util
# from image import ImageUpload
from palette import Palette
# from util import TicToc
# import glob
from searchable_collection import \
  SearchableImageCollectionExact, \
  SearchableImageCollectionFLANN

from collection import ImageCollection



dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), './data2'))
image_list_name = 'test1'
algorithm = 'flann'
sic_class = SearchableImageCollectionFLANN
distance_metric = 'euclidean'
sigma=16
num_dimensions=0
filename = os.path.join(dirname, '{}_{}_{}_{}_{}.pickle'.format(
image_list_name, algorithm, distance_metric, sigma, num_dimensions))

palette=Palette(num_hues=10, sat_range=2, light_range=3)
ic=ImageCollection(palette)
sic=sic_class(ic, distance_metric, sigma, num_dimensions)
sic.save(filename)


i=0;



