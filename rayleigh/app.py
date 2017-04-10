# -*-coding: UTF-8 -*-
import matplotlib
matplotlib.use('Agg')

import numpy as np
import simplejson as json
from bson import json_util
import cStringIO as StringIO
from skimage.io import imsave
from flask import Flask, render_template, request, make_response, send_file, redirect, url_for, Markup
import sys
import os
from urllib2 import unquote
from werkzeug.utils import secure_filename
from ainit import create_app
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


repo_dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, repo_dirname)
import rayleigh
import rayleigh.util as util

app = Flask(__name__)
app = create_app(app)
#app.debug = False  # TODO: make sure this is False in production
app.debug = True
UPLOAD_FOLDER='static/Uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'gif', 'bmp', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def make_json_response(body, status_code=200):
    print 'body:', body
    resp = make_response(json.dumps(body, default=json_util.default))
    resp.status_code = status_code
    resp.mimetype = 'application/json'
    return resp


"""
Load the Searchable Image Collections that can be used to search.
"""
fname_dict = {
    # 'data/testImage_Exact_euclidean_0_0.pickle': (
    #     'Chi-square, sigma=16, Exact', rayleigh.SearchableImageCollectionExact),
    # 'data/test1_Exact_euclidean_0_0.pickle': (
    #     'Chi-square, sigma=16, Exact', rayleigh.SearchableImageCollectionExact),
    # 'data/flickr_100K_exact_chi_square_16_0.pickle': (
    #     'Chi-square, sigma=16, Exact', rayleigh.SearchableImageCollectionExact),
    # 'data/flickr_100K_flann_chi_square_16_0.pickle': (
    #     'Chi-square, sigma=16, FLANN', rayleigh.SearchableImageCollectionFLANN),
    # 'data/flickr_100K_exact_manhattan_8_0.pickle': (
    #     'Manhattan, sigma=8, Exact', rayleigh.SearchableImageCollectionExact),
    # 'data/flickr_100K_exact_manhattan_16_0.pickle': (
    #     'Manhattan, sigma=16, Exact', rayleigh.SearchableImageCollectionExact),
    # 'data/flickr_100K_flann_manhattan_16_0.pickle': (
    #     'Manhattan, sigma=16, FLANN', rayleigh.SearchableImageCollectionFLANN),
    # 'data/flickr_100K_exact_euclidean_8_0.pickle': (
    #     'Euclidean, sigma=8, Exact', rayleigh.SearchableImageCollectionExact),
    # 'data/flickr_100K_exact_euclidean_16_0.pickle': (
    #     'Euclidean, sigma=16, Exact', rayleigh.SearchableImageCollectionExact),
    # 'data/flickr_100K_flann_euclidean_16_0.pickle': (
    #     'Euclidean, sigma=16, FLANN', rayleigh.SearchableImageCollectionFLANN),
    # 'data/flickr_100K_CKDTree_manhattan_16_0.pickle': (
    #     'Manhattan, sigma=16, CKDTree', rayleigh.SearchableImageCollectionCKDTree),
    # 'data/flickr_100K_CKDTree_euclidean_16_0.pickle': (
    #     'Euclidean, sigma=16, CKDTree', rayleigh.SearchableImageCollectionCKDTree),
    # 'data/test1_CKDTree_euclidean_16_0.pickle': (
    #     'Euclidean, sigma=16, CKDTree', rayleigh.SearchableImageCollectionCKDTree),
    # 'data/test1_flann_euclidean_16_0.pickle': (
    #     'euclidean, sigma=16, FLANN', rayleigh.SearchableImageCollectionFLANN),
    # 'data/test1_Exact_euclidean_16_0.pickle': (
    #     'Euclidean, sigma=16, Exact', rayleigh.SearchableImageCollectionExact),
    'data/test1_CKDTree_euclidean_16_0.pickle': (
        'Euclidean, sigma=16, CKDTree', rayleigh.SearchableImageCollectionCKDTree),


}

sics = {}
for fname in fname_dict.keys():
    full_fname = os.path.join(repo_dirname, fname)
    if os.path.exists(full_fname):
        name, cls = fname_dict[fname]
        print name,'111111', cls
        sics[name] = cls.load(os.path.join(full_fname))
if sics:
    default_sic_type = sics.keys()[0]
else:
    default_sic_type = None

"""
Set the default smoothing parameter applied to the color palette queries.
"""
sigmas = [8, 16, 20]
default_sigma = 16
features = ['color', 'colorSpatial', 'colorMap']
default_feature = 'color'
texture = ['yes', 'no']
default_texture = 'no'


@app.route('/')
def index():
    return redirect(url_for(
        'search_by_palette', sic_type=default_sic_type, sigma=default_sigma))


def parse_colors_and_values():
    """
    Parse the GET request string for the palette query information.
    The query string looks like "?colors=#ffffff,#000000&values=0.5,0.5

    Returns
    -------
    colors : dict of hex color strings to their nromalized value, or None
    """
    colors = request.args.get('colors', '')
    print(request.args)

    if len(colors) < 1:
        return None
    colors = unquote(colors).split(',')

    values = request.args.get('values', '')

    if len(values) < 1:
        values = np.ones(len(colors), 'float') / len(colors)
    else:
        values = np.array(unquote(values).split(','), 'float') / sum(np.array(unquote(values).split(','), 'float'))
    
    assert(len(values) == len(colors))
    return dict(zip(colors, values.tolist()))


@app.route('/search_by_palette')
def search_by_palette_default():
    return redirect(url_for(
        'search_by_palette', sic_type=default_sic_type, sigma=default_sigma))


@app.route('/search_by_palette/<sic_type>/<int:sigma>')
def search_by_palette(sic_type, sigma):
    colors = parse_colors_and_values()
    print colors
    return render_template(
        'search_by_palette.html',
        sic_types=sorted(sics.keys()), sic_type=sic_type,
        sigmas=sigmas, sigma=sigma,
        colors=Markup(json.dumps(colors)))


@app.route('/search_by_palette_json/<sic_type>/<int:sigma>')
def search_by_palette_json(sic_type, sigma):
    sic = sics[sic_type]
    colors = parse_colors_and_values()
    if colors is None:
        return make_json_response({'message': 'no request data'}, 400)
    pq = rayleigh.PaletteQuery(colors)
    color_hist = util.histogram_colors_smoothed(
        pq.lab_array, sic.ic.palette, sigma=sigma, direct=False)
    b64_hist = util.output_histogram_base64(color_hist, sic.ic.palette)
    results, time_elapsed = sic.search_by_color_hist(color_hist, 10)
    return make_json_response({
        'results': results, 'time_elapsed': time_elapsed, 'pq_hist': b64_hist})


@app.route('/search_by_image/<sic_type>/<fea_type>/<tex_type>/<image_id>')
def search_by_image(sic_type, fea_type, tex_type, image_id):
    # TODO: don't rely on the two methods below in the template, but render
    # images directly here.
    image = sics[sic_type].ic.get_image(image_id, no_hist=True)
    return render_template(
        'search_by_image.html',
        sic_types=sorted(sics.keys()), sic_type=sic_type,
        image_url=image['url'], image_id=image_id, features=features, fea_type=fea_type, texture=['yes', 'no', 'cnn'], tex_type=tex_type)


@app.route('/search_by_image_json/<sic_type>/<fea_type>/<tex_type>/<image_id>')
def search_by_image_json(sic_type,fea_type, tex_type,image_id):
    sic = sics[sic_type]
    if fea_type == 'color':
        query_data, results, time_elapsed = sic.search_by_image_in_dataset(image_id, 'color', tex_type, 100)
    elif fea_type == 'colorSpatial':
        query_data, results, time_elapsed = sic.search_by_image_in_dataset(image_id, 'colorSpatial', tex_type, 100)
    elif fea_type == 'colorMap':
        query_data, results, time_elapsed = sic.search_by_image_in_dataset(image_id, 'colorMap', tex_type, 100)
    return make_json_response({
        'results': results, 'time_elapsed': time_elapsed})


@app.route('/image_histogram/<sic_type>/<int:sigma>/<image_id>.png')
def get_image_histogram(sic_type, sigma, image_id):
    """
    Return png of the image histogram.

    Parameters
    ----------
    sic_type: string

    sigma: int
        If given as 0, return histogram as smoothed by the SIC.
        If given as 1, return unsmoothed histogram.
        If otherwise given, get the unsmoothed histogram and smooth manually.

    image_id: string

    Returns
    -------
    strIO: binary of a png file.
    """
    sic = sics[sic_type]
    if sigma == 0:
        hist = sic.get_image_hist(image_id)
    else:
        hist = sic.ic.get_image(image_id)['hist']
        if sigma != 1:
            hist = util.smooth_histogram(hist, sic.ic.palette, sigma)
    strIO = rayleigh.util.output_plot_for_flask(hist, sic.ic.palette)
    return send_file(strIO, mimetype='image/png')


@app.route('/palette_image/<sic_type>/<image_id>.png')
def get_palette_image(sic_type, image_id):
    sic = sics[sic_type]
    hist = sic.ic.get_image(image_id)['hist']
    img = rayleigh.util.color_hist_to_palette_image(hist, sic.ic.palette)
    strIO = StringIO.StringIO()
    imsave(strIO, img, plugin='pil', format_str='png')
    strIO.seek(0)
    return send_file(strIO, mimetype='image/png')


@app.route('/similar_to/<sic_type>/<image_id>')
def get_similar_images(sic_type, image_id):
    sic = sics[sic_type]
    hist = sic.ic.hists[int(image_id), :]
    data = sic.search_by_color_hist(hist, 10)
    return make_json_response(data)


@app.route('/search_by_upload')
def search_by_upload_default():
    return redirect(url_for(
        'search_by_upload', sic_type=default_sic_type, fea_type=default_feature, tex_type=default_texture, sigma=default_sigma))


@app.route('/search_by_upload/<sic_type>/<fea_type>/<int:sigma>')
def search_by_upload(sic_type,fea_type, sigma):
    colors = parse_colors_and_values()
    print colors
    return render_template(
        'search_by_upload.html',
        sic_types=sorted(sics.keys()), sic_type=sic_type,
        sigmas=sigmas, sigma=sigma, features=features, fea_type=fea_type, texture=texture, tex_type=default_texture)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    sic_type = request.values['sic_type']
    sigma = int(request.values['sigma'])
    fea_type = request.values['fea_type']
    tex_type = request.values['tex_type']
    sic = sics[sic_type]
    file = request.files['myPhoto'];
    if file and allowed_file(file.filename):
        fname=secure_filename(file.filename)
        img = rayleigh.ImageUpload(file)
        dui=img.dui
        dui= "data:image/png;base64,"+dui
        if fea_type == 'color':
            color_hist = util.histogram_colors_smoothed(
            img.lab_array, sic.ic.palette, sigma=sigma, direct=False)
            color_hist = color_hist.tolist()
        elif fea_type == 'colorSpatial':
            color_hist = util.histogram_colors_smoothed(
            img.lab_array, sic.ic.palette, sigma=sigma, direct=False)
            color_hist = color_hist.tolist()
        elif fea_type == 'colorMap':
            # 颜色直方图
            color_hist = util.histogram_colors_smoothed(
            img.lab_array, sic.ic.palette, sigma=sigma, direct=False)
            color_hist = color_hist.tolist()
            # 颜色分布图
        color_map = img.spatial_color_map_feature(sic.ic.palette)
        hash = img.get_texture()
        spa_color_hist = img.get_spatial_features()
    return render_template(
        'search_by_upload.html',
        sic_types=sorted(sics.keys()), sic_type=sic_type,
        sigmas=sigmas, sigma=sigma,
        color_hist=color_hist, hash=hash, color_map=color_map.tolist(),spa_color_hist=spa_color_hist, dui=dui, features=features, fea_type=fea_type, texture=texture, tex_type=tex_type)


@app.route('/draw_image', methods=['POST'])
def draw_image():
    sic_type = request.values['sic_type']
    image_dui = request.values['image']
    sigma = int(request.values['sigma'])
    fea_type = request.values['fea_type']
    tex_type = request.values['tex_type']
    sic = sics[sic_type]
    image = str(image_dui[22::]).decode('base64')
    img = open('./image/imgout.png', 'wb')
    img.write(image)
    img.close()
    if os.path.exists('./image/imgout.png'):
        img = rayleigh.ImageUpload('./image/imgout.png')
        if fea_type == 'color':
            color_hist = util.histogram_colors_smoothed(
                img.lab_array, sic.ic.palette, sigma=sigma, direct=False)
            color_hist = color_hist.tolist()
        elif fea_type == 'colorSpatial':
            color_hist = util.histogram_colors_smoothed(
                img.lab_array, sic.ic.palette, sigma=sigma, direct=False)
            color_hist = color_hist.tolist()

        elif fea_type == 'colorMap':
            # 颜色直方图
            color_hist = util.histogram_colors_smoothed(
            img.lab_array, sic.ic.palette, sigma=sigma, direct=False)
            color_hist = color_hist.tolist()
            # 颜色分布图
        spa_color_hist = img.get_spatial_features()
        color_map = img.spatial_color_map_feature(sic.ic.palette)
        hash = img.get_texture()
        os.remove('./image/imgout.png')
    return render_template(
        'show_draw_image.html',
        sic_types=sorted(sics.keys()), sic_type=sic_type,
        sigmas=sigmas, sigma=sigma,
        color_hist=color_hist,spa_color_hist = spa_color_hist, hash=hash, color_map=color_map.tolist(), dui=image_dui, features=features, fea_type=fea_type, texture=texture, tex_type=tex_type)


@app.route('/upload_image_json/<sic_type>/<fea_type>/<tex_type>/<int:sigma>')
def upload_image_json(sic_type, fea_type, tex_type, sigma):
    sic = sics[sic_type]
    color_hist = request.args.get('color_hist', '')
    if color_hist is "":
        return make_json_response({'message': 'no request data'}, 400)
    hash = request.args.get('hash', '')
    color_map = request.args.get('color_map', '')
    spa_color_hist = request.args.get('spa_color_hist', '')
    if hash is "":
        return make_json_response({'message': 'no request data'}, 400)
    color_hist=np.array(unquote(color_hist[1:-1]).split(','), 'float')
    spa_color_hist =np.array(unquote(spa_color_hist[1:-1]).split(','), 'float')
    color_map = np.array(unquote(color_map[2:-2]).replace('], [', ', ').split(','), 'float').reshape([13, 64])
    b64_hist = util.output_histogram_base64(color_hist, sic.ic.palette)
    if fea_type == 'color':
        if tex_type == 'no':
            results, time_elapsed = sic.search_by_color_hist(color_hist, 100)
        else:
            results, time_elapsed = sic.search_by_color_hist_texture(color_hist, hash, 100)
    elif fea_type == 'colorSpatial':
        if tex_type == 'no':
            results, time_elapsed = sic.search_by_color_spatial_hist(color_hist, spa_color_hist,100)
        else:
            # results, time_elapsed = sic.search_by_color_spatial_hist_texture(color_hist, spa_color_hist, hash, 100)
            results, time_elapsed = sic.search_by_color_spatial_hist(color_hist, spa_color_hist,100)
    elif fea_type == 'colorMap':
        if tex_type == 'no':
            results, time_elapsed = sic.search_by_color_map(color_hist, color_map, 100)
        else:
            results, time_elapsed = sic.search_by_color_hist_texture(color_hist, hash, 100)
    return make_json_response({
        'results': results, 'time_elapsed': time_elapsed, 'pq_hist': b64_hist})


@app.route('/search_by_drawing')
def search_by_drawing_default():
    return redirect(url_for(
        'search_by_drawing', sic_type=default_sic_type, fea_type=default_feature, tex_type=default_texture, sigma=default_sigma))


@app.route('/search_by_drawing/<sic_type>/<fea_type>/<int:sigma>')
def search_by_drawing(sic_type, fea_type, sigma):
    colors = parse_colors_and_values()
    print colors
    return render_template(
        'search_by_drawing.html',
        sic_types=sorted(sics.keys()), sic_type=sic_type,
        sigmas=sigmas, sigma=sigma,  features=features, fea_type=fea_type,texture=texture, tex_type=default_texture)


@app.route('/modify_image/<sic_type>/<image_id>')
def modify_image(sic_type,image_id):
    image = sics[sic_type].ic.get_image(image_id, no_hist=True)
    root = os.path.dirname(__file__)
    img = rayleigh.ImageModify(root+image['url'],image['id'])
    return render_template(
        'modify_image.html', image_url=img.dui)

if __name__ == '__main__':
    app.run(debug=True)
