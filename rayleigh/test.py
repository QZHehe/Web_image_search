"""
    color pickle
"""
import sys
import os
from palette import Palette
# import rayleigh.pyflann as pyflann
from collection import ImageCollection
# from pymongo import MongoClient
# from palette import Palette
from searchable_collection import \
  SearchableImageCollectionExact, \
  SearchableImageCollectionFLANN, \
  SearchableImageCollectionCKDTree



dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data2'))
image_list_name = 'flickr_100K'
algorithm = 'CKDTree'
sic_class = SearchableImageCollectionCKDTree
distance_metric = 'euclidean'
sigma=16
num_dimensions=0
filename = os.path.join(dirname, '{}_{}_{}_{}_{}.pickle'.format(
image_list_name, algorithm, distance_metric, sigma, num_dimensions))

palette=Palette(num_hues=10, sat_range=2, light_range=3)
ic=ImageCollection(palette)
sic=sic_class(ic, distance_metric, sigma, num_dimensions)
sic.save(filename)
#
i=0