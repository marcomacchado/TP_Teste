from flask import Blueprint, request, jsonify
from .models import TaskManager

task_bp = Blueprint('tasks', __name__)
task_manager = TaskManager()

@task_bp.route('/', methods=['GET'])
def list_tasks():
    completed = request.args.get('completed')
    if completed is not None:
        completed = completed.lower() == 'true'
    tasks = task_manager.get_tasks(completed=completed)
    return jsonify(tasks), 200

@task_bp.route('/', methods=['POST'])
def add_task():
    data = request.json
    description = data.get('description')
    category = data.get('category', 'General')
    deadline = data.get('deadline')

    if category not in TaskManager.CATEGORIES:
        return jsonify({"error": "Categoria inválida"}), 400

    task = task_manager.add_task(description, category, deadline)
    if task:
        return jsonify(task), 201
    return jsonify({"error": "Erro ao adicionar tarefa"}), 500

@task_bp.route('/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    data = request.json
    task = task_manager.edit_task(
        task_id,
        description=data.get('description'),
        category=data.get('category'),
        deadline=data.get('deadline')
    )
    if task:
        return jsonify(task), 200
    return jsonify({"error": "Task not found"}), 404

@task_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task_manager.delete_task(task_id)
    return jsonify({"message": f"Task {task_id} deleted"}), 200

@task_bp.route('/<int:task_id>/complete', methods=['PATCH'])
def mark_completed(task_id):
    task = task_manager.mark_completed(task_id)
    if task:
        return jsonify(task), 200
    return jsonify({"error": "Task not found"}), 404