# tests/test_e2e_todos_api.py

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_e2e_create_read_update_delete_todo():
    # 1. Создание задачи (Create)
    create_payload = {
        "title": "E2E Task",
        "description": "Created in E2E test",
        "completed": False,
    }
    r_create = requests.post(f"{BASE_URL}/todos", json=create_payload)
    assert r_create.status_code in (200, 201)

    todo = r_create.json()
    todo_id = todo["id"]

    # 2. Проверка, что задача появилась в списке (Read list)
    r_list = requests.get(f"{BASE_URL}/todos")
    assert r_list.status_code == 200
    todos = r_list.json()
    ids = {item["id"] for item in todos}
    assert todo_id in ids

    # 3. Получение задачи по id (Read one)
    r_get = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert r_get.status_code == 200
    todo_data = r_get.json()
    assert todo_data["title"] == create_payload["title"]
    assert todo_data["description"] == create_payload["description"]

    # 4. Обновление задачи (Update)
    update_payload = {
        "title": "E2E Task Updated",
        "description": "Updated in E2E test",
        # если в схеме есть completed — добавить его,
        # если нет, оставляем только title/description
    }
    r_update = requests.put(f"{BASE_URL}/todos/{todo_id}", json=update_payload)
    assert r_update.status_code == 200
    updated = r_update.json()
    assert updated["id"] == todo_id
    assert updated["title"] == update_payload["title"]
    assert updated["description"] == update_payload["description"]

    # 5. Удаление задачи (Delete)
    r_delete = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    assert r_delete.status_code in (200, 204)

    # 6. Проверка, что задача больше недоступна (404)
    r_get_after_delete = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert r_get_after_delete.status_code == 404


def test_e2e_validation_and_errors():
    # 1. Попытка создания задачи без обязательного поля title
    invalid_payload = {
        "description": "No title here",
        "completed": False,
    }
    r_invalid = requests.post(f"{BASE_URL}/todos", json=invalid_payload)
    # FastAPI для ошибок валидации возвращает 422
    assert r_invalid.status_code == 422
    body = r_invalid.json()
    assert "detail" in body

    # 2. Попытка получить несуществующую задачу
    r_not_found = requests.get(f"{BASE_URL}/todos/999999")
    assert r_not_found.status_code == 404

    # 3. Попытка обновить несуществующую задачу
    update_payload = {
        "title": "Ghost task",
        "description": "Should not exist",
    }
    r_update_missing = requests.put(f"{BASE_URL}/todos/999999", json=update_payload)
    # в зависимости от реализации: 404 или другая ошибка
    assert r_update_missing.status_code in (404, 400)
