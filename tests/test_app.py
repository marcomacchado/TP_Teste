import pytest  
from app import create_app
from app.models import TaskManager
import os
import json

# Fixture para resetar o estado antes de cada teste
@pytest.fixture
def reset_tasks():
    # Remove o arquivo JSON antes de cada teste
    if os.path.exists("tasks.json"):
        os.remove("tasks.json")
    # Recria o arquivo vazio
    with open("tasks.json", "w") as file:
        json.dump([], file)

@pytest.fixture
def client(reset_tasks):  # Usa a fixture de reset
    app = create_app()
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def task_manager(reset_tasks):  # Usa a fixture de reset
    task_manager = TaskManager()
    task_manager.tasks = []  # Reseta a lista de tarefas
    task_manager.save_tasks()  # Salva o estado limpo
    return task_manager

# Teste 1: Listar tarefas quando não há nenhuma
def test_list_tasks_empty(client):
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.get_json() == []

# Teste 2: Adicionar uma nova tarefa
def test_add_task(client):
    task_data = {"description": "Estudar Python", "category": "Estudo", "deadline": "2025-12-31"}
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 201
    task = response.get_json()
    assert task["description"] == "Estudar Python"
    assert task["completed"] is False

# Teste 3: Listar tarefas após adicionar uma
def test_list_tasks_after_adding(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    response = client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 1

# Teste 4: Editar uma tarefa existente
def test_edit_task(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    response = client.put("/tasks/1", json={"description": "Tarefa Editada"})
    assert response.status_code == 200
    assert response.get_json()["description"] == "Tarefa Editada"

# Teste 5: Editar tarefa inexistente
def test_edit_nonexistent_task(client):
    response = client.put("/tasks/999", json={"description": "Inexistente"})
    assert response.status_code == 404

# Teste 6: Deletar uma tarefa existente
def test_delete_task(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task 1 deleted"

# Teste 7: Deletar tarefa inexistente
def test_delete_nonexistent_task(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 200  # O sistema trata como sucesso

# Teste 8: Marcar uma tarefa como concluída
def test_mark_task_completed(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    response = client.patch("/tasks/1/complete")
    assert response.status_code == 200
    task = response.get_json()
    assert task["completed"] is True

# Teste 9: Marcar tarefa inexistente como concluída
def test_mark_nonexistent_task_completed(client):
    response = client.patch("/tasks/999/complete")
    assert response.status_code == 404

# Teste 10: Listar tarefas pendentes
def test_list_pending_tasks(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    client.post("/tasks/", json={"description": "Tarefa 2"})
    client.patch("/tasks/1/complete")  # Concluir a primeira tarefa
    response = client.get("/tasks/?completed=false")
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Tarefa 2"

# Teste 11: Listar tarefas concluídas
def test_list_completed_tasks(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    client.patch("/tasks/1/complete")
    response = client.get("/tasks/?completed=true")
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Tarefa 1"

# Teste 12: Adicionar tarefa sem descrição
def test_add_task_without_description(client):
    response = client.post("/tasks/", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Description is required"

# Teste 13: Adicionar tarefa com categoria personalizada
def test_add_task_with_category(client):
    task_data = {"description": "Ler um livro", "category": "Lazer"}
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 201
    assert response.get_json()["category"] == "Lazer"

# Teste 14: Persistência de dados entre requisições
def test_task_persistence(client):
    task_data = {"description": "Persistência", "deadline": "2025-12-31"}
    client.post("/tasks/", json=task_data)
    response = client.get("/tasks/")
    assert len(response.get_json()) == 1

# Teste 15: Validação de id único para tarefas
def test_unique_task_ids(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    client.post("/tasks/", json={"description": "Tarefa 2"})
    tasks = client.get("/tasks/").get_json()
    assert tasks[0]["id"] != tasks[1]["id"]