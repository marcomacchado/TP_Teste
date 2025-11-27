import pytest
from app import create_app, db
from app.models import TaskManager, Task
from datetime import datetime

@pytest.fixture
def app():
    return create_app('testing')

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture
def task_manager(app):
    with app.app_context():
        return TaskManager(db) 

# Teste 1: Listar tarefas quando não há nenhuma
def test_list_tasks_empty(client):
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.get_json() == []

# Teste 2: Adicionar uma nova tarefa
def test_add_task_e2e(client): 
    task_data = {
        "description": "Estudar Python",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 201

    response_get = client.get("/tasks/")
    assert response_get.status_code == 200
    tasks = response_get.get_json()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Estudar Python"
    assert tasks[0]["category"] == "Pessoal"
    assert tasks[0]["deadline"] == "2025-12-31"
    assert tasks[0]["completed"] is False


# Teste 3: Listar tarefas após adicionar uma
def test_list_tasks_after_adding(client):
    task_data = {
        "description": "Estudar Python",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    client.post("/tasks/", json=task_data)
    response = client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 1


# Teste 4: Editar uma tarefa existente
def test_edit_task(client):
    task_data = {
        "description": "Estudar Python",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 201
    created_task = response.get_json()
    task_id = created_task["id"]
    assert task_id == 1

    edited_task_data = {
        "description": "Tarefa Editada",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    put_response = client.put(f"/tasks/{task_id}", json=edited_task_data)
    assert put_response .status_code == 200
    edited_task = put_response.get_json()
    assert edited_task["description"] == "Tarefa Editada"


# Teste 5: Marcar uma tarefa como concluída
def test_mark_task_completed(client):
    task_data = {
        "description": "Estudar Python",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    client.post("/tasks/", json=task_data)
    response = client.patch("/tasks/1/complete")
    assert response.status_code == 200
    task = response.get_json()
    assert task["completed"] is True


# Teste 6: Editar tarefa inexistente
def test_edit_nonexistent_task(client):
    task_data = {
        "description": "Inexistente",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    response = client.put("/tasks/999", json=task_data)
    assert response.status_code == 404


# Teste 7: Deletar uma tarefa existente
def test_delete_task(client):
    client.post("/tasks/", json={"description": "Tarefa 1"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task 1 deleted"


# Teste 8: Deletar tarefa inexistente
def test_delete_nonexistent_task(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 200  # O sistema trata como sucesso


# Teste 9: Marcar tarefa inexistente como concluída
def test_mark_nonexistent_task_completed(client):
    response = client.patch("/tasks/999/complete")
    assert response.status_code == 404


# Teste 10: Listar tarefas pendentes
def test_list_pending_tasks(client):
    client.delete("/tasks/clear")
    task_1_data = {
        "description": "Tarefa 1",
        "category": "Pessoal",
        "deadline": "2025-12-30",
    }
    task_2_data = {
        "description": "Tarefa 2",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    client.post("/tasks/", json=task_1_data)
    client.post("/tasks/", json=task_2_data)
    client.patch("/tasks/1/complete")  # Concluir a primeira tarefa
    response = client.get("/tasks/?completed=false")
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Tarefa 2"


# Teste 11: Listar tarefas concluídas
def test_list_completed_tasks(client):
    client.delete("/tasks/clear")
    response_before = client.get("/tasks/?completed=true")
    tasks_before = response_before.get_json()
    num_completed_before = len(tasks_before)

    task_data = {
        "description": "Tarefa 3",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    client.post("/tasks/", json=task_data)
    client.patch("/tasks/1/complete")

    response_after = client.get("/tasks/?completed=true")
    tasks_after = response_after.get_json()
    num_completed_after = len(tasks_after)

    assert num_completed_after == num_completed_before + 1
    assert any(task["description"] == "Tarefa 3" for task in tasks_after)


# Teste 12: Adicionar tarefa sem descrição
def test_add_task_without_description(client):
    response = client.post("/tasks/", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Description is required"


# Teste 13: Adicionar tarefa com categoria personalizada
def test_add_task_with_category(client):
    client.delete("/tasks/clear")
    task_data = {
        "description": "Ler um livro",
        "category": "Lazer",
    }  # Categoria inválida
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 400  # Espera o código de status 400
    assert response.get_json()["error"] == "Categoria inválida"


# Teste 14: Persistência de dados entre requisições
def test_task_persistence(client):
    client.delete("/tasks/clear")
    task_data = {
        "description": "Estudar Python",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    client.post("/tasks/", json=task_data)
    response = client.get("/tasks/")
    assert len(response.get_json()) == 1


# Teste 15: Validação de id único para tarefas
def test_unique_task_ids(client):
    client.delete("/tasks/clear")
    task_1_data = {
        "description": "Tarefa 1",
        "category": "Pessoal",
        "deadline": "2025-12-30",
    }
    task_2_data = {
        "description": "Tarefa 2",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    client.post("/tasks/", json=task_1_data)
    client.post("/tasks/", json=task_2_data)
    tasks = client.get("/tasks/").get_json()
    assert tasks[0]["id"] != tasks[1]["id"]

# Teste 16: Tentar adicionar tarefa incompleta (sem categoria ou prazo) deve falhar
def test_add_task_incomplete_fails(client):
    client.delete("/tasks/clear")
    response = client.post("/tasks/", json={"description": "Tarefa incompleta"})
    assert response.status_code == 400

# Teste 17: Limpar tarefas em um banco já vazio
def test_clear_tasks_on_empty_database(client):
    client.delete("/tasks/clear")
    clear_response = client.delete("/tasks/clear")
    assert clear_response.status_code == 200
    data = clear_response.get_json()
    assert data["message"] == "All tasks deleted"

    list_response = client.get("/tasks/")
    assert list_response.status_code == 200
    assert list_response.get_json() == []

# Teste 18: Deletar uma tarefa entre várias mantém as demais
def test_delete_one_of_multiple_tasks(client):
    client.delete("/tasks/clear")
    t1 = client.post("/tasks/", json={
        "description": "Tarefa 1", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()
    t2 = client.post("/tasks/", json={
        "description": "Tarefa 2", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()

    delete_response = client.delete(f"/tasks/{t1['id']}")
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == f"Task {t1['id']} deleted"

    tasks = client.get("/tasks/").get_json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == t2["id"]
    assert tasks[0]["description"] == "Tarefa 2"

# Teste 19: Marcar uma tarefa como concluída duas vezes é idempotente
def test_mark_task_completed_twice_is_idempotent(client):
    client.delete("/tasks/clear")
    task = client.post(
        "/tasks/",
        json={
            "description": "Tarefa idempotente",
            "category": "Pessoal",
            "deadline": "2025-12-31",
        },
    ).get_json()

    first = client.patch(f"/tasks/{task['id']}/complete")
    assert first.status_code == 200
    assert first.get_json()["completed"] is True

    second = client.patch(f"/tasks/{task['id']}/complete")
    assert second.status_code == 200
    assert second.get_json()["completed"] is True

# Teste 20: Marcar como concluída uma tarefa já deletada retorna 404
def test_mark_deleted_task_completed_returns_404(client):
    client.delete("/tasks/clear")
    task = client.post("/tasks/", json={
        "description": "Tarefa 1", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()

    client.delete(f"/tasks/{task['id']}")
    response = client.patch(f"/tasks/{task['id']}/complete")
    assert response.status_code == 404

# Teste 21: Adicionar tarefa com categoria válida 'Trabalho'
def test_add_task_with_trabalho_category(client):
    client.delete("/tasks/clear")
    task_data = {
        "description": "Tarefa de trabalho",
        "category": "Trabalho",
        "deadline": "2025-12-31",
    }
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 201

    created_task = response.get_json()
    assert created_task["category"] == "Trabalho"
    assert created_task["description"] == "Tarefa de trabalho"

# Teste 22: Editar tarefa alterando a categoria de 'Pessoal' para 'Trabalho'
def test_edit_task_change_category(client):
    client.delete("/tasks/clear")
    task_data = {
        "description": "Tarefa",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    created = client.post("/tasks/", json=task_data).get_json()
    task_id = created["id"]

    updated_data = {
        "description": "Tarefa",
        "category": "Trabalho",
        "deadline": "2025-12-31",
    }
    response = client.put(f"/tasks/{task_id}", json=updated_data)
    assert response.status_code == 200

    updated_task = response.get_json()
    assert updated_task["category"] == "Trabalho"

# Teste 23: Editar com categoria inválida deve ser ignorado (mantém a anterior)
def test_edit_task_ignores_invalid_category(client):
    client.delete("/tasks/clear")
    task_data = {
        "description": "Tarefa",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    created = client.post("/tasks/", json=task_data).get_json()
    task_id = created["id"]

    updated_data = {
        "description": "Tarefa",
        "category": "Lazer",
        "deadline": "2025-12-31",
    }
    response = client.put(f"/tasks/{task_id}", json=updated_data)
    assert response.status_code == 200
    
    task_final = client.get("/tasks/").get_json()[0]
    assert task_final["category"] == "Pessoal"

# Teste 24: Listar tarefas pendentes quando não há nenhuma tarefa
def test_list_pending_tasks_when_empty(client):
    client.delete("/tasks/clear")
    response = client.get("/tasks/?completed=false")
    assert response.status_code == 200
    assert response.get_json() == []

# Teste 25: Listar tarefas concluídas quando não há nenhuma tarefa
def test_list_completed_tasks_when_empty(client):
    client.delete("/tasks/clear")
    response = client.get("/tasks/?completed=true")
    assert response.status_code == 200
    assert response.get_json() == []

# Teste 26: Filtro de pendentes e concluídas com três tarefas
def test_filter_pending_and_completed_with_three_tasks(client):
    client.delete("/tasks/clear")

    t1 = {"description": "T1", "category": "Pessoal", "deadline": "2025-12-30"}
    t2 = {"description": "T2", "category": "Pessoal", "deadline": "2025-12-31"}
    t3 = {"description": "T3", "category": "Pessoal", "deadline": "2026-01-01"}

    r1 = client.post("/tasks/", json=t1).get_json()
    r2 = client.post("/tasks/", json=t2).get_json()
    r3 = client.post("/tasks/", json=t3).get_json()

    client.patch(f"/tasks/{r1['id']}/complete")
    client.patch(f"/tasks/{r3['id']}/complete")

    completed = client.get("/tasks/?completed=true").get_json()
    pending = client.get("/tasks/?completed=false").get_json()

    assert {t["id"] for t in completed} == {r1["id"], r3["id"]}
    assert len(pending) == 1
    assert pending[0]["id"] == r2["id"]

# Teste 27: Listar todas as tarefas independentemente do status
def test_list_all_tasks_ignores_completion_status(client):
    client.delete("/tasks/clear")

    t1 = client.post("/tasks/", json={
        "description": "TA", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()

    t2 = client.post("/tasks/", json={
        "description": "TB", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()

    client.patch(f"/tasks/{t1['id']}/complete")

    response = client.get("/tasks/")
    tasks = response.get_json()
    assert len(tasks) == 2
    ids = {t["id"] for t in tasks}
    assert ids == {t1["id"], t2["id"]}

# Teste 28: Limpar todas as tarefas remove pendentes e concluídas
def test_clear_all_tasks_with_completed_and_pending(client):
    client.delete("/tasks/clear")

    t1 = client.post("/tasks/", json={
        "description": "TA", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()

    t2 = client.post("/tasks/", json={
        "description": "TB", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()

    client.patch(f"/tasks/{t1['id']}/complete")

    clear_response = client.delete("/tasks/clear")
    assert clear_response.status_code == 200
    assert clear_response.get_json()["message"] == "All tasks deleted"

    assert client.get("/tasks/").get_json() == []

# Teste 29: Verificar campos retornados na representação da tarefa
def test_task_representation_fields(client):
    client.delete("/tasks/clear")
    task_data = {
        "description": "Verificar campos",
        "category": "Pessoal",
        "deadline": "2025-12-31",
    }
    client.post("/tasks/", json=task_data)

    tasks = client.get("/tasks/").get_json()
    assert len(tasks) == 1
    task = tasks[0]

    for field in ("id", "description", "category", "deadline", "completed"):
        assert field in task

# Teste 30: IDs das tarefas são inteiros
def test_task_ids_are_integers(client):
    client.delete("/tasks/clear")
    t1 = client.post("/tasks/", json={
        "description": "T1", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()
    t2 = client.post("/tasks/", json={
        "description": "T2", "category": "Pessoal", "deadline": "2025-12-31"
    }).get_json()

    assert isinstance(t1["id"], int)
    assert isinstance(t2["id"], int)


# ------------------------------ Testes e2e ------------------------------ 

# Teste E2E 1: Fluxo completo de criar, listar, editar e excluir uma tarefa
def test_e2e_full_task_lifecycle(client):
    task_data = {
        "description": "Estudar Engenharia de Dados",
        "category": "Pessoal",
        "deadline": "2025-01-31",
    }
    create_response = client.post("/tasks/", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.get_json()
    task_id = created_task["id"]

    list_response = client.get("/tasks/")
    tasks = list_response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id

    updated_task_data = {
        "description": "Estudar Python Avançado",
        "category": "Pessoal",
        "deadline": "2025-02-15",
    }
    edit_response = client.put(f"/tasks/{task_id}", json=updated_task_data)
    assert edit_response.status_code == 200
    updated_task = edit_response.get_json()
    assert updated_task["description"] == "Estudar Python Avançado"

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == f"Task {task_id} deleted"

    final_list_response = client.get("/tasks/")
    assert final_list_response.get_json() == []


# Teste E2E 2: Criar múltiplas tarefas e verificar a listagem de pendentes e concluídas
def test_e2e_list_pending_and_completed(client):
    # Criar duas tarefas
    task_1 = {"description": "Ler um livro", "category": "Pessoal", "deadline": "2025-01-15"}
    task_2 = {"description": "Exercícios físicos", "category": "Pessoal", "deadline": "2025-01-20"}
    client.post("/tasks/", json=task_1)
    client.post("/tasks/", json=task_2)

    client.patch("/tasks/1/complete")

    pending_response = client.get("/tasks/?completed=false")
    pending_tasks = pending_response.get_json()
    assert len(pending_tasks) == 1
    assert pending_tasks[0]["description"] == "Exercícios físicos"

    completed_response = client.get("/tasks/?completed=true")
    completed_tasks = completed_response.get_json()
    assert len(completed_tasks) == 1
    assert completed_tasks[0]["description"] == "Ler um livro"


# Teste E2E 3: Fluxo de criar uma tarefa com validação de erro
def test_e2e_create_task_with_validation_error(client):
    response = client.post("/tasks/", json={"category": "Pessoal", "deadline": "2025-01-31"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Description is required"


# Teste E2E 4: Fluxo de persistência de dados entre requisições
def test_e2e_persistence_across_requests(client):
    task_data = {
        "description": "Aprender Flask",
        "category": "Trabalho",
        "deadline": "2025-01-20",
    }
    client.post("/tasks/", json=task_data)

    response = client.get("/tasks/")
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Aprender Flask"


# Teste E2E 5: Fluxo de limpar todas as tarefas
def test_e2e_clear_all_tasks(client):
    task_1 = {"description": "Estudar", "category": "Pessoal", "deadline": "2025-01-10"}
    task_2 = {"description": "Fazer compras", "category": "Pessoal", "deadline": "2025-01-11"}
    client.post("/tasks/", json=task_1)
    client.post("/tasks/", json=task_2)

    clear_response = client.delete("/tasks/clear")
    assert clear_response.status_code == 200
    assert clear_response.get_json()["message"] == "All tasks deleted"

    response = client.get("/tasks/")
    assert response.get_json() == []