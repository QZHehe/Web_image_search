# -*- coding: UTF-8 -*-
# encoding = utf-8
from flask import Blueprint
import os
import sys

auth = Blueprint('auth', __name__)

from . import views
repo_dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, repo_dirname)