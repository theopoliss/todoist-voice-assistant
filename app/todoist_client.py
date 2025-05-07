from todoist_api_python.api import TodoistAPI
from config import settings

api = TodoistAPI(settings.todoist_api_token)

def create_task(content: str, due_string: str | None = None, **kwargs):
    return api.add_task(content=content, due_string=due_string, **kwargs)

def update_task(task_id: str, **patch):
    return api.update_task(task_id=task_id, **patch)

def delete_task(task_id: str):
    return api.delete_task(task_id)