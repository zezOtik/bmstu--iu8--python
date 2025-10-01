"""Helpers for testing."""
import os
import pytest

DIR_PATH = os.path.dirname(__file__)
FILES_DIR = os.path.join(DIR_PATH, 'resources')


@pytest.fixture()
def filepath():
    """Returns full file path for test files."""

    def make_filepath(filename):
        return os.path.join(FILES_DIR, filename)
    return make_filepath


@pytest.fixture()
def load_file(filepath):
    """Opens filename with encoding and return its contents."""

    def make_load_file(filename, encoding='utf-8'):
        with open(filepath(filename), encoding=encoding) as f:
            return f.read().strip()
    return make_load_file


@pytest.fixture()
def get_stream(filepath):
    def make_stream(filename, encoding='utf-8'):
        return open(filepath(filename), encoding=encoding)
    return make_stream
