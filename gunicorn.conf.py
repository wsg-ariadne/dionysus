from multiprocessing import cpu_count
from os import path


wsgi_app = 'main:app'
bind = '0.0.0.0:5000'
workers = cpu_count() * 2
