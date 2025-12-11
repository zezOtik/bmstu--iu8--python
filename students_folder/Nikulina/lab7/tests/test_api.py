import pytest
import yaml
import httpx
from datetime import datetime, UTC

BASE_URL = "http://127.0.0.1:8000"

with open("tests/expected_responses.yaml", "r", encoding="utf-8") as f:
    expected = yaml.safe_load(f)

@pytest.mark.asyncio
async def test_habits_api():

    async with httpx.AsyncClient() as client:

        add_payload = {
            "user_id": 1,
            "name": "Drink water",
            "description": "2 liters per day"
        }

        response = await client.post(f"{BASE_URL}/habits/add", params=add_payload)
        assert response.status_code == 200
        assert "id" in response.json()

        expected["add_habit_response"]["id"] = response.json()["id"]

        response = await client.get(f"{BASE_URL}/habits/all")
        assert response.status_code == 200

        habits = response.json()
        assert len(habits) > 0

        expected["get_habits_response"][0]["id"] = habits[0]["id"]

        assert habits[0]["user_id"] == expected["get_habits_response"][0]["user_id"]
        assert habits[0]["name"] == expected["get_habits_response"][0]["name"]
        assert habits[0]["description"] == expected["get_habits_response"][0]["description"]

        habit_id = habits[0]["id"]

        completion_payload = {
            "habit_id": habit_id,
            "date": datetime.now(UTC).isoformat().replace("+00:00", "Z")
        }

        response = await client.post(
            f"{BASE_URL}/habits/complete",
            params=completion_payload
        )

        assert response.status_code == 200

        completion_id = response.json()["id"]
        expected["add_completion_response"]["id"] = completion_id

        response = await client.get(f"{BASE_URL}/habits/{habit_id}/completions")
        assert response.status_code == 200

        completions = response.json()
        assert len(completions) > 0

        assert completions[0]["habit_id"] == habit_id
        assert "date" in completions[0]

        response = await client.get(f"{BASE_URL}/habits/{habit_id}/streak")
        assert response.status_code == 200

        streak = response.json()
        assert "streak" in streak
        assert isinstance(streak["streak"], int)
