import logging

import pytest
from pydantic import ValidationError

from students_folder.Borodin.LabaMore1.lab_1 import UserSpec

logger = logging.getLogger("test_User")


@pytest.mark.borodin_lab3
def test_class_profile(yaml_test_data):
    test_cases = yaml_test_data("Borodin/lab_3/UserSpec.yaml")
    for test_desc, value, answer in test_cases:
        logger.info(f"Testing: {test_desc}")
        try:
            test_class = UserSpec.model_validate(value)
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