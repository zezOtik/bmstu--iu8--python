import logging

import pytest
from pydantic import ValidationError

from students_folder.melnikova.lab2 import OrdersSpec

@pytest.mark.melnikova_lab3
def test_class_order_spec(yaml_test_data):
    test_cases = yaml_test_data("melnikova/lab3/OrderSpec.yaml")
    for test_desc, value, answer in test_cases:
        logger = logging.getLogger("test_OderSpec")
        logger.info(f"Testing: {test_desc}")
        try:
            test_class = OrderSpec.model_validate(value)
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