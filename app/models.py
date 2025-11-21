from app import db  
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.description}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category,
            "deadline": self.deadline.strftime("%Y-%m-%d") if self.deadline else None,  # Trata caso de deadline nulo
            "completed": self.completed,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

class TaskManager:
    CATEGORIES = ["Trabalho", "Pessoal", "Casa", "Saúde", "Finanças"]

    def __init__(self, db):
        self.db = db  # Injeta a instância do SQLAlchemy

    def add_task(self, description, category, deadline):
        deadline_datetime = datetime.strptime(deadline, "%Y-%m-%d")
        new_task = Task(description=description, category=category, deadline=deadline_datetime)
        self.db.session.add(new_task)
        self.db.session.commit()
        return new_task.to_dict()

    def edit_task(self, task_id, description=None, category=None, deadline=None):
        task = Task.query.get(task_id)
        if task:
            if description:
                task.description = description
            if category and category in self.CATEGORIES:
                task.category = category
            if deadline:
                deadline_datetime = datetime.strptime(deadline, "%Y-%m-%d")
                task.deadline = deadline_datetime
            self.db.session.commit()
            return task
        return None

    def delete_task(self, task_id):
        task = Task.query.get(task_id)
        if task:
            self.db.session.delete(task)
            self.db.session.commit()

    def mark_completed(self, task_id):
        task = Task.query.get(task_id)
        if task:
            task.completed = True
            self.db.session.commit()
        return task

    def get_tasks(self, completed=None):
        query = Task.query
        if completed is not None:
            query = query.filter_by(completed=completed)
        return query.order_by(Task.deadline.nulls_first(), Task.deadline).all()
    
    def delete_all(self):
        self.db.session.query(Task).delete()
        self.db.session.commit()