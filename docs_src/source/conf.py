import os
import sys

# Добавляем корень проекта в sys.path, чтобы можно было импортировать students_folder
sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'bmstu_python_iu8'
copyright = '2025, ZMV'
author = 'ZMV'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',      # добавляет ссылки на исходный код
    'sphinx.ext.napoleon',      # поддержка Google/NumPy docstring
]

templates_path = ['_templates']
exclude_patterns = ['../build']

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
