import pytest
import logging
from pydantic import ValidationError
from students_folder.melnikova.lab2 import OrdersSpec

logger = logging.getLogger(__name__)


@pytest.mark.maa_lab3
def test_class_orders_spec(yaml_test_data):
    """Тест OrdersSpec с данными из YAML"""
    test_cases = yaml_test_data("Melnikova/lab3/OrdersSpec.yaml")

    for test_desc, value, expected_answer in test_cases:
        logger = logging.getLogger("test_OrdersSpec")
        logger.info(f"Testing: {test_desc}")

        try:
            # Пытаемся создать объект OrdersSpec
            orders = OrdersSpec.model_validate(value)
            actual_answer = True
            logger.info(f" Validation succeeded for: {test_desc}")
        except ValidationError as e:
            actual_answer = False
            logger.info(f" Validation failed for: {test_desc} - {e}")

        # Проверяем, что результат соответствует ожидаемому
        assert actual_answer == expected_answer, (
            f"Test '{test_desc}' failed: expected {expected_answer}, got {actual_answer}\n"
            f"Value: {value}"
        )
        logger.info(f" Test '{test_desc}' passed")