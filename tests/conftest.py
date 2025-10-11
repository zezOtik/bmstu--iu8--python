"""Helpers for testing."""

import os

import pytest
import yaml

DIR_PATH = os.path.dirname(__file__)
FILES_DIR = os.path.join(DIR_PATH, "src")


def pytest_configure(config):
    config.addinivalue_line("markers", "zmv_lab1: mark test as part of zmv's test")
    config.addinivalue_line("markers", "zaa_lab3: mark test as part of zaa's test")


@pytest.fixture()
def filepath():
    """Returns full file path for test files."""

    def make_filepath(filename):
        return os.path.join(FILES_DIR, filename)

    return make_filepath


@pytest.fixture()
def load_file(filepath):
    """Opens filename with encoding and return its contents."""

    def make_load_file(filename, encoding="utf-8"):
        with open(filepath(filename), encoding=encoding) as f:
            return f.read().strip()

    return make_load_file


@pytest.fixture()
def get_stream(filepath):
    def make_stream(filename, encoding="utf-8"):
        return open(filepath(filename), encoding=encoding)

    return make_stream


@pytest.fixture()
def read_yaml():
    """Fixture for reading YAML files."""
    
    def _read_yaml(file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                pytest.fail(f"Failed to load YAML file {file_path}: {exc}")
    
    return _read_yaml


@pytest.fixture()
def yaml_test_data(filepath, read_yaml):
    """Fixture for getting test data from YAML files."""
    
    def _get_test_data(filename: str):
        file_path = filepath(filename)
        test_yaml = read_yaml(file_path)
        
        if "answerList" not in test_yaml:
            pytest.fail(f"YAML file {filename} must contain 'answerList' key")
        
        test_cases = []
        for item in test_yaml["answerList"]:
            if not all(key in item for key in ["test_desc", "value", "answer"]):
                pytest.fail(f"Each test case must have 'test_desc', 'value', and 'answer' keys")
            
            test_cases.append((item["test_desc"], item["value"], item["answer"]))
        
        return test_cases
    
    return _get_test_data
