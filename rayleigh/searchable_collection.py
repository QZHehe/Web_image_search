# -*- coding: UTF-8 -*-
# encoding = utf-8
"""
Methods to search an ImageCollection with brute force, exhaustive search.
"""

import cgi
import abc
import cPickle
import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import \
    manhattan_distances, euclidean_distances, additive_chi2_kernel
import rayleigh.pyflann as pyflann
from scipy.spatial import cKDTree

import util
from image import Image

from rayleigh.util import TicToc
tt = TicToc()


class SearchableImageCollection(object):
    """
    Initialize with a rayleigh.ImageCollection, a distance_metric, and the
    number of dimensions to reduce the histograms to.

    Parameters
    ----------
    image_collection : rayleigh.ImageCollection
    dist_metric : string
        must be in self.DISTANCE_METRICS
    sigma : nonnegative float
        Amount of smoothing applied to histograms.
        If 0, none.
    num_dimensions : int
        number of dimensions to reduce the histograms to, using PCA.
        If 0, do not reduce dimensions.
    """
    def __init__(self, image_collection, dist_metric, sigma, num_dimensions):
        self.ic = image_collection
        print 'get id ind map'
        self.id_ind_map = self.ic.get_id_ind_map()
        print 'get id ind map end'
        self.distance_metric = dist_metric
        if self.distance_metric not in self.DISTANCE_METRICS:
            raise Exception("Unsupported distance metric.")
        self.num_dimensions = num_dimensions
        print 'get_hist'
        self.hists_reduced = self.ic.get_hists()
        print 'get_hist end'
        # self.spa_hists_reduced = self.ic.get_spatial_hists()
        self.sigma = sigma
        if self.sigma > 0:
            print 'smooth'
            self.smooth_histograms()
            print 'smooth end'
        if self.num_dimensions > 0:
            self.reduce_dimensionality()

    @staticmethod
    def load(filename):
        """
        Load ImageCollection from filename.
        """
        return cPickle.load(open(filename, 'rb'))

    def save(self, filename):
        """
        Save self to filename.
        """
        cPickle.dump(self, open(filename, 'w'), 2)

    def smooth_histograms(self):
        """
        Smooth histograms with a Gaussian.
        """
        for i in range(self.hists_reduced.shape[0]):
            color_hist = self.hists_reduced[i, :]
            self.hists_reduced[i, :] = util.smooth_histogram(
                color_hist, self.ic.palette, self.sigma)
            print i

    def reduce_dimensionality(self):
        """
        Compute and store PCA dimensionality-reduced histograms.
        """
        tt.tic('reduce_dimensionality')
        self.pca = PCA(n_components=self.num_dimensions, whiten=True)
        self.pca.fit(self.hists_reduced)
        self.hists_reduced = self.pca.transform(self.hists_reduced)
        tt.toc('reduce_dimensionality')

    def get_image_hist(self, img_id):
        """
        Return the smoothed image histogram of the image with the given id.

        Parameters
        ----------
        img_id : string

        Returns
        -------
        color_hist : ndarray
        """
        img_ind = self.id_ind_map[img_id]
        color_hist = self.hists_reduced[img_ind, :]
        return color_hist

    def get_image_spatial_hist(self, img_id):
        """
        Return the smoothed image histogram of the image with the given id.

        Parameters
        ----------
        img_id : string

        Returns
        -------
        color_hist : ndarray
        """
        img_ind = self.id_ind_map[img_id]
        color_hist = self.spa_hists_reduced[img_ind, :]
        return color_hist

    def search_by_image_in_dataset(self, img_id, feature, texture,num=20):
        """
        Search images in database for similarity to the image with img_id in
        the database.

        See search_by_color_hist() for implementation.

        Parameters
        ----------
        img_id : string
        num : int, optional

        Returns
        -------
        query_img_data : dict
        results : list
            list of dicts of nearest neighbors to query
        """
        query_img_data = self.ic.get_image(img_id, no_hist=True)
        if feature == 'color':
            if texture == 'no':
                color_hist = self.get_image_hist(img_id)
                results, time_elapsed = self.search_by_color_hist(color_hist, num, reduced=True)
            elif texture =='cnn':
                cnn = np.array([cPickle.loads(self.ic.get_hash(img_id, no_hist=True)['cnn_feature'])])
                color_hist = self.get_image_hist(img_id)
                results, time_elapsed = self.search_by_color_hist_cnn(color_hist, cnn[0], num, reduced=True)
            else:
                hash = str(self.ic.get_hash(img_id, no_hist=True)['hash'])
                color_hist = self.get_image_hist(img_id)
                results, time_elapsed = self.search_by_color_hist_texture(color_hist, hash, num, reduced=True)
        elif feature == 'colorSpatial':
            # if texture == 'no':
                # color_hist = self.get_image_spatial_hist(img_id)
                # color_hist= np.array(color_hist, 'float')
                # results, time_elapsed = self.search_by_color_spatial_hist(color_hist, num, reduced=True)
            # elif texture =='cnn':
                # cnn = np.array([cPickle.loads(self.ic.get_hash(img_id, no_hist=True)['cnn_feature'])])
                # color_hist = self.get_image_spatial_hist(img_id)
                # color_hist = np.array(color_hist, 'float')
                # results, time_elapsed = self.search_by_color_spatial_hist_cnn(color_hist, cnn[0], num, reduced=True)
            # else:
                # hash = str(self.ic.get_hash(img_id, no_hist=True)['hash'])
                # color_hist = self.get_image_spatial_hist(img_id)
                # color_hist= np.array(color_hist, 'float')
                # results, time_elapsed = self.search_by_color_spatial_hist_texture(color_hist, hash, num, reduced=True)
            color_hist = self.get_image_hist(img_id)
            spa_color_hist = np.array([cPickle.loads(self.ic.get_spa_hist(img_id, no_hist=True)['spa_hist'])])[0]
            results, time_elapsed = self.search_by_color_spatial_hist(color_hist, spa_color_hist, 100)
        elif feature == 'colorMap':
            if texture == 'no':
                color_map = self.ic.get_hash(img_id, no_hist=True)['color_map']
                color_hist = self.get_image_hist(img_id)
                results, time_elapsed = self.search_by_color_map(color_hist, color_map, 100)
            else:
                hash = str(self.ic.get_hash(img_id, no_hist=True)['hash'])
                color_hist = self.get_image_hist(img_id)
                results, time_elapsed = self.search_by_color_hist_texture(color_hist, hash, num, reduced=True)


        return query_img_data, results, time_elapsed

    def search_by_image(self, image_filename, num=20):
        """
        Search images in database by color similarity to image.
        
        See search_by_color_hist().
        """
        query_img = Image(image_filename)
        color_hist = util.histogram_colors_smoothed(
            query_img.lab_array, self.ic.palette,
            sigma=self.sigma, direct=False)
        results, time_elapsed = self.search_by_color_hist(color_hist)
        return query_img.as_dict(), results, time_elapsed

    def search_by_color_hist(self, color_hist, num=20, reduced=False):
        """
        Search images in database by color similarity to the given histogram.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        num : int, optional
            number of nearest neighbors to ret
        reduced : boolean, optional
            is the given color_hist already reduced in dimensionality?

        Returns
        -------
        query_img : dict
            info about the query image
        results : list
            list of dicts of nearest neighbors to query
        """
        if self.num_dimensions > 0 and not reduced:
            color_hist = self.pca.transform(color_hist)
        tt.tic('nn_ind')
        nn_ind, nn_dists = self.nn_ind(color_hist, num, 'color_hist')
        time_elapsed = tt.qtoc('nn_ind')
        results = []
        # TODO: tone up the amount of data returned: don't need resized size,
        # _id, maybe something else?
        tt.tic('find')
        for ind, dist in zip(nn_ind, nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_image(img_id, no_hist=True)
            img['url'] = cgi.escape(img['url'])
            # img['url'] = img['url']
            img['distance'] = dist
            results.append(img)
        print  tt.qtoc('find')
        return results, time_elapsed



    def search_by_color_hist_texture(self, color_hist, hash,num=20, reduced=False):
        """
        Search images in database by color and texture similarity to the given histogram.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        hash
        num : int, optional
            number of nearest neighbors to ret,
        reduced : boolean, optional
            is the given color_hist already reduced in dimensionality?

        Returns
        -------
        query_img : dict
            info about the query image
        results : list
            list of dicts of nearest neighbors to query
        """
        if self.num_dimensions > 0 and not reduced:
            color_hist = self.pca.transform(color_hist)
        tt.tic('nn_ind')
        nn_ind, nn_dists = self.nn_ind(color_hist, num, 'color_hist')
        time_elapsed = tt.qtoc('nn_ind')
        # according texture to reorder
        # nn_ind2, nn_dists2 = self.tex_ind()
        # get hash
        hashs = []
        for ind, dist in zip(nn_ind, nn_dists):
            img_id = self.id_ind_map[ind]
            img = str(self.ic.get_hash(img_id, no_hist=True)['hash'])
            hashs.append(img)
        diff = np.array([util.diff(hash, i) for i in hashs])
        hash_result = np.argsort(diff)
        hash_nn_ind = nn_ind[hash_result]
        hash_nn_dists = nn_dists[hash_result]
        results = []
        # TODO: tone up the amount of data returned: don't need resized size,
        # _id, maybe something else?
        for ind, dist in zip(hash_nn_ind, hash_nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_image(img_id, no_hist=True)
            img['url'] = cgi.escape(img['url'])
            # img['url'] = img['url']
            img['distance'] = dist
            results.append(img)
        return results, time_elapsed

    def search_by_color_hist_cnn(self, color_hist, cnn ,num=20, reduced=False):
        """
        Search images in database by color and texture similarity to the given histogram.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        hash
        num : int, optional
            number of nearest neighbors to ret,
        reduced : boolean, optional
            is the given color_hist already reduced in dimensionality?

        Returns
        -------
        query_img : dict
            info about the query image
        results : list
            list of dicts of nearest neighbors to query
        """
        if self.num_dimensions > 0 and not reduced:
            color_hist = self.pca.transform(color_hist)
        tt.tic('nn_ind')
        nn_ind, nn_dists = self.nn_ind(color_hist, num, 'color_hist')
        time_elapsed = tt.qtoc('nn_ind')
        # according texture to reorder
        # nn_ind2, nn_dists2 = self.tex_ind()
        # get hash
        cnns = []
        for ind, dist in zip(nn_ind, nn_dists):
            img_id = self.id_ind_map[ind]
            img = np.array([cPickle.loads(self.ic.get_hash(img_id, no_hist=True)['cnn_feature'])])[0]
            cnns.append(img)
        cnns = np.array(cnns)
        diff = np.dot(cnn, cnns.T)
        hash_result = np.argsort(-diff)
        hash_nn_ind = nn_ind[hash_result]
        hash_nn_dists = nn_dists[hash_result]
        results = []
        # TODO: tone up the amount of data returned: don't need resized size,
        # _id, maybe something else?
        for ind, dist in zip(hash_nn_ind, hash_nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_image(img_id, no_hist=True)
            img['url'] = cgi.escape(img['url'])
            # img['url'] = img['url']
            img['distance'] = dist
            results.append(img)
        return results, time_elapsed

    def search_by_color_spatial_hist_texture(self, spatial_hist, hash, num=3, reduced=False):
        """
        Search images in database by color similarity to the given histogram.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        num : int, optional
            number of nearest neighbors to ret
        reduced : boolean, optional
            is the given color_hist already reduced in dimensionality?

        Returns
        -------
        query_img : dict
            info about the query image
        results : list
            list of dicts of nearest neighbors to query
        """
        if self.num_dimensions > 0 and not reduced:
            spatial_hist = self.pca.transform(spatial_hist)
        tt.tic('nn_ind')
        nn_ind, nn_dists = self.nn_ind(spatial_hist, num, 'spatial_hist')
        time_elapsed = tt.qtoc('nn_ind')

        hashs = []
        for ind, dist in zip(nn_ind, nn_dists):
            img_id = self.id_ind_map[ind]
            img = str(self.ic.get_hash(img_id, no_hist=True)['hash'])
            hashs.append(img)
        diff = np.array([util.diff(hash, i) for i in hashs])
        hash_result = np.argsort(diff)
        hash_nn_ind = nn_ind[hash_result]
        hash_nn_dists = nn_dists[hash_result]

        results = []
        # TODO: tone up the amount of data returned: don't need resized size,
        # _id, maybe something else?
        for ind, dist in zip(hash_nn_ind, hash_nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_image(img_id, no_hist=True)
            img['url'] = cgi.escape(img['url'])
            img['distance'] = dist
            results.append(img)
        return results, time_elapsed

    def search_by_color_spatial_hist_cnn(self, spatial_hist, cnn, num=3, reduced=False):
        """
        Search images in database by color similarity to the given histogram.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        num : int, optional
            number of nearest neighbors to ret
        reduced : boolean, optional
            is the given color_hist already reduced in dimensionality?

        Returns
        -------
        query_img : dict
            info about the query image
        results : list
            list of dicts of nearest neighbors to query
        """
        if self.num_dimensions > 0 and not reduced:
            spatial_hist = self.pca.transform(spatial_hist)
        tt.tic('nn_ind')
        nn_ind, nn_dists = self.nn_ind(spatial_hist, num, 'spatial_hist')
        time_elapsed = tt.qtoc('nn_ind')

        # get hash
        cnns = []
        for ind, dist in zip(nn_ind, nn_dists):
            img_id = self.id_ind_map[ind]
            img = np.array([cPickle.loads(self.ic.get_hash(img_id, no_hist=True)['cnn_feature'])])[0]
            cnns.append(img)
        cnns = np.array(cnns)
        diff = np.dot(cnn, cnns.T)
        hash_result = np.argsort(-diff)
        hash_nn_ind = nn_ind[hash_result]
        hash_nn_dists = nn_dists[hash_result]
        results = []
        # TODO: tone up the amount of data returned: don't need resized size,
        # _id, maybe something else?
        for ind, dist in zip(hash_nn_ind, hash_nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_image(img_id, no_hist=True)
            img['url'] = cgi.escape(img['url'])
            img['distance'] = dist
            results.append(img)
        return results, time_elapsed

    def search_by_color_spatial_hist(self, color_hist, spatial_hist, num, reduced=False):
        """
        Search images in database by color similarity to the given histogram.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        num : int, optional
            number of nearest neighbors to ret
        reduced : boolean, optional
            is the given color_hist already reduced in dimensionality?

        Returns
        -------
        query_img : dict
            info about the query image
        results : list
            list of dicts of nearest neighbors to query
        """
        # if self.num_dimensions > 0 and not reduced:
        #     spatial_hist = self.pca.transform(spatial_hist)
        # tt.tic('nn_ind')
        # nn_ind, nn_dists = self.nn_ind(spatial_hist, num, 'spatial_hist')
        # time_elapsed = tt.qtoc('nn_ind')
        # results = []
        # # TODO: tone up the amount of data returned: don't need resized size,
        # # _id, maybe something else?
        # for ind, dist in zip(nn_ind, nn_dists):
        #     img_id = self.id_ind_map[ind]
        #     img = self.ic.get_image(img_id, no_hist=True)
        #     img['url'] = cgi.escape(img['url'])
        #     img['distance'] = dist
        #     results.append(img)
        if self.num_dimensions > 0 and not reduced:
            color_hist = self.pca.transform(color_hist)
        tt.tic('nn_ind')
        nn_ind, nn_dists = self.nn_ind(color_hist, num, 'color_hist')
        time_elapsed = tt.qtoc('nn_ind')
        # according texture to reorder
        # nn_ind2, nn_dists2 = self.tex_ind()
        # get hash
        spa_hists = []
        for ind, dist in zip(nn_ind, nn_dists):
            img_id = self.id_ind_map[ind]
            img = np.array([cPickle.loads(self.ic.get_spa_hist(img_id, no_hist=True)['spa_hist'])])[0]
            spa_hists.append(img)
        spa_hists = np.array(spa_hists)
        diff = euclidean_distances(spatial_hist, spa_hists)
        spa_result = np.argsort(diff[0])
        spa_nn_ind = nn_ind[spa_result]
        spa_nn_dists = nn_dists[spa_result]
        results = []
        # TODO: tone up the amount of data returned: don't need resized size,
        # _id, maybe something else?
        for ind, dist in zip(spa_nn_ind, spa_nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_image(img_id, no_hist=True)
            img['url'] = cgi.escape(img['url'])
            # img['url'] = img['url']
            img['distance'] = dist
            results.append(img)
        return results, time_elapsed

    # 颜色空间分布
    def search_by_color_map(self, color_hist, color_map, num=20, reduced=False):
        """
        Search images in database by color and texture similarity to the given histogram.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        hash
        num : int, optional
            number of nearest neighbors to ret,
        reduced : boolean, optional
            is the given color_hist already reduced in dimensionality?

        Returns
        -------
        query_img : dict
            info about the query image
        results : list
            list of dicts of nearest neighbors to query
        """
        if self.num_dimensions > 0 and not reduced:
            color_hist = self.pca.transform(color_hist)
        tt.tic('nn_ind')
        nn_ind, nn_dists = self.nn_ind(color_hist, num, 'color_hist')
        time_elapsed = tt.qtoc('nn_ind')
        # according texture to reorder
        # nn_ind2, nn_dists2 = self.tex_ind()
        # get color_map
        color_maps = []
        for ind, dist in zip(nn_ind, nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_hash(img_id, no_hist=True)['color_map']
            color_maps.append(img)
        #?
        diff = np.array([util.color_map_feature_distance(color_map, np.array(i)) for i in color_maps])
        color_map_result = np.argsort(-diff)
        color_map_nn_ind = nn_ind[color_map_result]
        color_map_nn_dists = nn_dists[color_map_result]
        results = []
        # TODO: tone up the amount of data returned: don't need resized size,
        # _id, maybe something else?
        for ind, dist in zip(color_map_nn_ind, color_map_nn_dists):
            img_id = self.id_ind_map[ind]
            img = self.ic.get_image(img_id, no_hist=True)
            img['url'] = cgi.escape(img['url'])
            # img['url'] = img['url']
            img['distance'] = dist
            results.append(img)
        return results, time_elapsed



    @abc.abstractmethod
    def nn_ind(self, color_hist, num):
        """
        Return num closest nearest neighbors (potentially approximate) to the
        query color_hist, and the distances to them.

        Override this search method in extending classes.

        Parameters
        ----------
        color_hist : (K,) ndarray
            histogram over the color palette
        num : int
            number of nearest neighbors to return.

        Returns
        -------
        nn_ind : (num,) ndarray
            Indices of the neighbors in the dataset.

        nn_dists (num,) ndarray
            Distances to the neighbors returned.
        """
        pass


class SearchableImageCollectionExact(SearchableImageCollection):
    """
    Search the image collection exhaustively (mainly through np.dot).
    """

    DISTANCE_METRICS = ['manhattan', 'euclidean', 'chi_square']

    def nn_ind(self, color_hist, num, feature):
        """
        Exact nearest neighbor seach through exhaustive comparison.
        """
        if feature == 'color_hist':
            features = self.hists_reduced
        elif feature == 'spatial_hist':
            features = self.spa_hists_reduced

        if self.distance_metric == 'manhattan':
            dists = manhattan_distances(color_hist, features)
        elif self.distance_metric == 'euclidean':
            dists = euclidean_distances(color_hist, features, squared=True)
        elif self.distance_metric == 'chi_square':
            dists = -additive_chi2_kernel(color_hist, features)
        
        dists = dists.flatten()
        nn_ind = np.argsort(dists).flatten()[:num]
        nn_dists = dists[nn_ind]
        
        return nn_ind, nn_dists


class SearchableImageCollectionFLANN(SearchableImageCollection):
    """
    Search the image collection using the FLANN library for aNN indexing.
    
    The FLANN index is built with automatic tuning of the search algorithm,
    which can take a while (~90s on 25K images).
    """

    DISTANCE_METRICS = ['manhattan', 'euclidean', 'chi_square']

    @staticmethod
    def load(filename):
        # Saving the flann object results in memory errors, so we use its own
        # method to save its index in a separate file.
        sic = cPickle.load(open(filename))
        return sic.build_index([filename + '_flann_index_n_spa', filename + '_flann_index_spa'])

    def save(self, filename):
        # See comment in load().
        # flann = self.n_spa.flann
        # self.n_spa.flann = None
        # cPickle.dump(self, open(filename, 'w'), 2)
        # flann.save_index(filename + '_flann_index_n_spa')
        # self.n_spa.flann = flann
        #
        # flann2 = self.spa.flann
        # self.spa.flann = None
        # cPickle.dump(self, open(filename, 'w'), 2)
        # flann2.save_index(filename + '_flann_index_spa')
        # self.spa.flann = flann2
        flann = self.n_spa_flann
        self.n_spa_flann = None
        # flann2 = self.spa_flann
        # self.spa_flann = None
        cPickle.dump(self, open(filename, 'w'), 2)
        flann.save_index(filename + '_flann_index_n_spa')
        # flann2.save_index(filename + '_flann_index_spa')
        self.n_spa_flann = flann
        # self.spa_flann = flann2

    def __init__(self, image_collection, distance_metric, sigma, dimensions):
        super(SearchableImageCollectionFLANN, self).__init__(
            image_collection, distance_metric, sigma, dimensions)
        print 'build_index'
        self.build_index()
        print 'build_index end'

    def build_index(self, index_filename=None):
        tt.tic('build_index')
        pyflann.set_distance_type(self.distance_metric)
        self.n_spa_flann = pyflann.FLANN()
        # self.spa_flann = pyflann.FLANN()
        if index_filename:
            self.n_spa_flann.load_index(index_filename[0], self.hists_reduced)
            # self.spa_flann.load_index(index_filename[1], self.spa_hists_reduced)
        else:
            self.params = self.n_spa_flann.build_index(
                self.hists_reduced, algorithm='autotuned',
                sample_fraction=0.98, target_precision=0.98,
                build_weight=0.01, memory_weight=0.)
            # self.spa_params = self.flann.build_index(
            #     self.spa_hists_reduced, algorithm='autotuned',
            #     sample_fraction=0.3, target_precision=.8,
            #     build_weight=0.01, memory_weight=0.)
            # self.spa_params = self.spa_flann.build_index(
            #     self.spa_hists_reduced, algorithm='autotuned',
            #     sample_fraction=1, target_precision=1,
            #     build_weight=0.01, memory_weight=0.)
        # print(self.params, self.spa_params)
        print(self.params)
        tt.toc('build_index')
        return self

    def nn_ind(self, color_hist, num, feature):
        if feature == 'color_hist':
            nn_ind, nn_dists = self.n_spa_flann.nn_index(
                color_hist, num, checks=self.params['checks'])
        elif feature == 'spatial_hist':
            nn_ind, nn_dists = self.spa_flann.nn_index(
                color_hist, num, checks=self.spa_params['checks'])

        return nn_ind.flatten(), nn_dists.flatten()


class SearchableImageCollectionCKDTree(SearchableImageCollection):
    """
    Use the cKDTree data structure from scipy.spatial for the index.

    Parameters:
        - LEAF_SIZE (int): The number of points at which the algorithm switches
            over to brute-force.
        - EPS (non-negative float): Parameter for query(), such that the
            k-th returned value is guaranteed to be no further than (1 + eps)
            times the distance to the real k-th nearest neighbor.

    NOTE: These parameters have not been tuned.
    """

    DISTANCE_METRICS = ['manhattan', 'euclidean']
    Ps = {'manhattan': 1, 'euclidean': 2}
    LEAF_SIZE = 5
    EPSILON = 1

    @staticmethod
    def load(filename):
        return cPickle.load(open(filename)).build_index()

    def __init__(self, image_collection, distance_metric, sigma, dimensions):
        super(SearchableImageCollectionCKDTree, self).__init__(
            image_collection, distance_metric, sigma, dimensions)
        self.build_index()

    def build_index(self):
        tt.tic('build_index_ckdtree')
        self.ckdtree = cKDTree(self.hists_reduced, self.LEAF_SIZE)
        self.p = self.Ps[self.distance_metric]
        tt.toc('build_index_ckdtree')

        # tt.tic('build_spatial_index_ckdtree')
        # self.spa_ckdtree = cKDTree(self.spa_hists_reduced, self.LEAF_SIZE)
        # self.spa_p = self.Ps[self.distance_metric]
        # tt.toc('build_spatial_index_ckdtree')
        return self

    def nn_ind(self, color_hist, num, feature):
        if feature == 'color_hist':
            nn_dists, nn_ind = self.ckdtree.query(
                color_hist, num, eps=self.EPSILON, p=self.p)
        elif feature == 'spatial_hist':
            nn_dists, nn_ind = self.spa_ckdtree.query(
                color_hist, num, eps=self.EPSILON, p=self.spa_p)
        return nn_ind.flatten(), nn_dists.flatten()
