import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

project = 'Лабораторная работа 3'
copyright = '2025, Мельникова А.'
author = 'Мельникова Алиса'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

language = 'ru'