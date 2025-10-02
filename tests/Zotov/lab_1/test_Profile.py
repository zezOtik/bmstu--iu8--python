import logging

import pytest
from pydantic import ValidationError

from students_folder.Zotov_folder.lab_2.Profile import Profile
from tests.common_func import get_set

logger = logging.getLogger("test_Profile")


@pytest.mark.zmv_lab1
def test_class_profile(filepath):
    file = filepath("Zotov/lab_2/Profile.yaml")
    for test_desc, value, answer in get_set(file):
        logger.info(f"Testing: {test_desc}")
        try:
            test_class = Profile.model_validate(value)
            # Ожидаем answer = True
            test_answer = True
            assert (
                answer == test_answer
            ), f"Expected validation to fail for {test_desc}, but it passed"
            logger.info(f"{test_desc} PASSED - validation succeeded as expected")
        except ValidationError as e:
            # Ожидаем answer = False
            test_answer = False
            assert (
                answer == test_answer
            ), f"Expected validation to pass for {test_desc}, but got error: {e}"
            logger.info(f"{test_desc} PASSED - validation failed as expected: {e}")
