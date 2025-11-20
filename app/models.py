import json
import os

class TaskManager:
    FILE_PATH = "tasks.json"

    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as file:
                self.tasks = json.load(file)
        else:
            self.tasks = []

    def save_tasks(self):
        with open(self.FILE_PATH, 'w') as file:
            json.dump(self.tasks, file)

    def add_task(self, description, category, deadline):
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "category": category,
            "deadline": deadline,
            "completed": False
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def edit_task(self, task_id, description=None, category=None, deadline=None):
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if task:
            if description:
                task['description'] = description
            if category:
                task['category'] = category
            if deadline:
                task['deadline'] = deadline
            self.save_tasks()
        return task

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save_tasks()

    def mark_completed(self, task_id):
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if task:
            task['completed'] = True
            self.save_tasks()
        return task

    def get_tasks(self, completed=None):
        if completed is None:
            return self.tasks
        return [t for t in self.tasks if t['completed'] == completed]
