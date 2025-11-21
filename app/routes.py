from flask import Blueprint, request, jsonify
from .models import TaskManager
from app import db

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/', methods=['GET'])
def list_tasks():
    task_manager = TaskManager(db)
    completed = request.args.get('completed')
    if completed is not None:
        completed = completed.lower() == 'true'
    tasks = task_manager.get_tasks(completed=completed)
    task_list = [task.to_dict() for task in tasks]
    return jsonify(task_list), 200

@task_bp.route('/', methods=['POST'])
def add_task():
    task_manager = TaskManager(db)
    data = request.json
    description = data.get('description')
    category = data.get('category', 'General')  # 'General' será o padrão
    deadline = data.get('deadline')

    # Primeiro, verifique se a descrição foi fornecida
    if not description:
        return jsonify({"error": "Description is required"}), 400

    # Se a categoria não for válida, retorna um erro
    if category not in TaskManager.CATEGORIES:
        return jsonify({"error": "Categoria inválida"}), 400

    task = task_manager.add_task(description, category, deadline)
    if task:
        return jsonify(task), 201
    return jsonify({"error": "Erro ao adicionar tarefa"}), 500


@task_bp.route('/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    task_manager = TaskManager(db)
    data = request.json
    task = task_manager.edit_task(
        task_id,
        description=data.get('description'),
        category=data.get('category'),
        deadline=data.get('deadline')
    )
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict()), 200

@task_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task_manager = TaskManager(db)
    task_manager.delete_task(task_id)
    return jsonify({"message": f"Task {task_id} deleted"}), 200

@task_bp.route('/<int:task_id>/complete', methods=['PATCH'])
def mark_completed(task_id):
    task_manager = TaskManager(db)
    task = task_manager.mark_completed(task_id)
    if task:
        return jsonify(task.to_dict()), 200
    return jsonify({"error": "Task not found"}), 404

@task_bp.route('/clear', methods=['DELETE'])
def delete_all_tasks():
    task_manager = TaskManager(db)
    task_manager.delete_all()
    return jsonify({"message": "All tasks deleted"}), 200
