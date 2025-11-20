import unittest
from app import create_app
from app.models import TaskManager

class TestTaskRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.task_manager = TaskManager()
        self.task_manager.tasks = []

    def test_add_task(self):
        response = self.client.post('/tasks/', json={"description": "Task 1", "category": "Work", "deadline": "2024-12-31"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("Task 1", response.json['description'])

    def test_list_tasks(self):
        self.task_manager.add_task("Task 1", "Work", "2024-12-31")
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)

    def test_mark_completed(self):
        task = self.task_manager.add_task("Task 1", "Work", "2024-12-31")
        response = self.client.patch(f'/tasks/{task["id"]}/complete')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['completed'])

    def test_delete_task(self):
        task = self.task_manager.add_task("Task 1", "Work", "2024-12-31")
        response = self.client.delete(f'/tasks/{task["id"]}')
        self.assertEqual(response.status_code, 200)
