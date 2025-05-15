from todoist_api_python.api import TodoistAPI
from .config import settings
import traceback # Added for more detailed error logging

api = TodoistAPI(settings.todoist_api_token)

def create_task(content: str, due_string: str | None = None, priority: int | None = None, **kwargs):
    return api.add_task(content=content, due_string=due_string, priority=priority, **kwargs)

def update_task(task_id: str, **patch):
    return api.update_task(task_id=task_id, **patch)

def delete_task(task_id: str):
    return api.delete_task(task_id)

def find_tasks(query: str | None = None, project_id: str | None = None, label: str | None = None) -> list:
    """
    Finds tasks. If a query is provided, it searches the content of tasks.
    Filters by project_id or label if provided.
    Returns a list of simplified task dicts.
    """
    try:
        tasks_api_response = api.get_tasks(
            project_id=project_id,
            label=label
        )
        # print(f"DEBUG: tasks_api_response type: {type(tasks_api_response)}") # Optional
        # print(f"DEBUG: tasks_api_response: {tasks_api_response}") # Optional

        found_tasks = []
        if query:
            query_lower = query.lower()
            for task_item in tasks_api_response: 
                # ---- START DEBUG PRINT ----
                print(f"DEBUG: Processing task_item type: {type(task_item[0])}")
                print(f"DEBUG: TASK: {task_item[0].content}")
                try:
                    print(f"DEBUG: Task content: {task_item[0].content}")
                except AttributeError:
                    print(f"DEBUG: task_item has no 'content' attribute. Value: {task_item[0]}")
                # ---- END DEBUG PRINT ----
                
                if not hasattr(task_item[0], 'content') or not isinstance(task_item[0].content, str):
                    print(f"WARN: Skipping item, expected Task object with content string, got {type(task_item[0])}")
                    continue 

                if query_lower in task_item[0].content.lower():
                    found_tasks.append({
                        "id": task_item[0].id,
                        "content": task_item[0].content,
                        "due": str(task_item[0].due) if task_item[0].due else None
                    })
        else:
            for task_item in tasks_api_response: 
                if not hasattr(task_item[0], 'content') or not isinstance(task_item[0].content, str):
                    print(f"WARN: Skipping item in else block, expected Task object, got {type(task_item[0])}")
                    continue
                found_tasks.append({
                    "id": task_item[0].id,
                    "content": task_item[0].content,
                    "due": str(task_item[0].due) if task_item[0].due else None
                })
        return found_tasks
    except Exception as e:
        print(f"Error finding tasks: {e}") 
        traceback.print_exc() # Add full traceback for the original error
        return []