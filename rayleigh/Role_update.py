# -*- coding: UTF-8 -*-
# encoding = utf-8
from pymongo import MongoClient
# from collection import collection_user
from pymongo.errors import ConnectionFailure

def get_mongodb_collection():
    """
    Establish connection to MongoDB and return the relevant collection.

    Returns
    -------
    collection : pymongo.Collection
        Pymongo Collection of images and their histograms.
    """
    try:
        connection = MongoClient('localhost', 27666)
    except ConnectionFailure:
        raise Exception("Cannot instantiate ImageCollection without \
                         a MongoDB server running on port 27666")
    # return connection.image_collection.images
    return connection.image_collection.test1


# For parallel execution, function must be in module scope
collection = get_mongodb_collection()

def get_mongodb_collection2():
    """
    Establish connection to MongoDB and return the relevant collection.

    Returns
    -------
    collection : pymongo.Collection
        Pymongo Collection of images and their histograms.
    """
    try:
        connection = MongoClient('localhost', 27666)
    except ConnectionFailure:
        raise Exception("Cannot instantiate ImageCollection without \
                         a MongoDB server running on port 27666")
    # return connection.image_collection.images
    return connection.image_collection.test0303


# For parallel execution, function must be in module scope
collection_image = get_mongodb_collection2()

def get_mongodb_collection_user():
    """
    Establish connection to MongoDB and return the relevant collection.

    Returns
    -------
    collection : pymongo.Collection
        Pymongo Collection of images and their histograms.
    """
    try:
        connection = MongoClient('localhost', 27666)
    except ConnectionFailure:
        raise Exception("Cannot instantiate ImageCollection without \
                         a MongoDB server running on port 27666")
    # return connection.image_collection.images
    return connection.image_collection


# For parallel execution, function must be in module scope
collection_user = get_mongodb_collection_user()



class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role:
    db = collection_user.Role

    def __init__(self, name, permission, default):
        self.name = name
        self.permission = permission
        self.default = default

    def new_role(self):
        collection = {
            'name': self.name,
            'permissions': self.permission,
            'default': self.default
        }
        self.db.insert(collection)


def insert_role():
    roles = {
        'User': (Permission.FOLLOW |
                 Permission.COMMENT |
                 Permission.WRITE_ARTICLES, True),
        'Moderator': (Permission.FOLLOW |
                      Permission.COMMENT |
                      Permission.WRITE_ARTICLES |
                      Permission.MODERATE_COMMENTS, False),
        'Administrator': (0xff, False)
    }
    connect = collection_user.Role
    for i in roles:
        role = connect.find_one({'name': i})
        if role is None:
            Role(name=i, permission=roles[i][0], default=roles[i][1]).new_role()
        connect.update({'name': i}, {'$set': {'permissions': roles[i][0]}})
        connect.update({'name': i}, {'$set': {'default': roles[i][1]}})


insert_role()
