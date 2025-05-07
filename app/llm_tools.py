import json
from openai import OpenAI
from .config import settings
from app import todoist_client # Import your Todoist functions

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)

# Define the tools (functions) the LLM can use
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_todoist_task",
            "description": "Create a new task in Todoist based on user's request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content or description of the task (e.g., 'Buy groceries', 'Finish English paper').",
                    },
                    "due_string": {
                        "type": "string",
                        "description": "The due date and time for the task in natural language (e.g., 'tomorrow at 5pm', 'next Monday'). This is optional.",
                    },
                    # Add other parameters like priority here if desired, matching todoist_client.create_task kwargs
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_todoist_task",
            "description": "Update an existing task in Todoist. The user must specify the task content or some way to identify the task, which you should then try to map to a task_id if not provided directly. For updates, all parameters are optional except task_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to update. If the user doesn't provide an ID, you might need to ask for it or find it based on content.",
                    },
                    "content": {"type": "string", "description": "The new content for the task. Optional."},
                    "due_string": {"type": "string", "description": "The new due date for the task. Optional."},
                    # Add other updatable fields as needed
                },
                "required": ["task_id"], # Task_id is essential for the API call
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todoist_task",
            "description": "Delete a task from Todoist. The user must specify the task content or some way to identify the task, which you should then try to map to a task_id if not provided directly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to delete. If the user doesn't provide an ID, you might need to ask for it or find it based on content.",
                    },
                },
                "required": ["task_id"], # Task_id is essential for the API call
            },
        },
    }
]

async def handle_user(text: str) -> str:
    try:
        print(f"User input: {text}")
        completion = await client.chat.completions.create(
            model=settings.model,
            messages=[{"role": "user", "content": text}],
            tools=tools,
            tool_choice="auto", 
        )

        response_message = completion.choices[0].message
        print(f"LLM response message: {response_message}")

        # Check for tool_calls (newer API) or function_call (older API)
        tool_calls = response_message.tool_calls
        if not tool_calls and response_message.function_call: # Adapt for older function_call
            # Convert function_call to the tool_calls format for consistent handling
            tool_calls = [
                {
                    "id": "legacy_function_call", # Dummy ID
                    "type": "function",
                    "function": response_message.function_call
                }
            ]

        if tool_calls:
            results = []
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args_json = tool_call.function.arguments
                try:
                    function_args = json.loads(function_args_json)
                except json.JSONDecodeError:
                    results.append(f"Error: Invalid JSON arguments from LLM for {function_name}: {function_args_json}")
                    continue

                print(f"LLM wants to call function: {function_name} with args: {function_args}")

                action_result = ""
                if function_name == "create_todoist_task":
                    content = function_args.get("content")
                    due_string = function_args.get("due_string")
                    if not content:
                        action_result = "Error: Task content is missing."
                    else:
                        try:
                            task = todoist_client.create_task(content=content, due_string=due_string)
                            action_result = f"Task '{content}' created successfully (ID: {task.id})."
                        except Exception as e:
                            action_result = f"Error creating task in Todoist: {str(e)}"
                
                elif function_name == "update_todoist_task":
                    task_id = function_args.get("task_id")
                    if not task_id:
                        action_result = "Error: Task ID is missing for update."
                    else:
                        patch_args = {k: v for k, v in function_args.items() if k != 'task_id'}
                        if not patch_args:
                             action_result = "Error: No update parameters provided."
                        else:
                            try:
                                todoist_client.update_task(task_id=task_id, **patch_args)
                                action_result = f"Task ID '{task_id}' updated."
                            except Exception as e:
                                action_result = f"Error updating task {task_id}: {str(e)}"

                elif function_name == "delete_todoist_task":
                    task_id = function_args.get("task_id")
                    if not task_id:
                        action_result = "Error: Task ID is missing for delete."
                    else:
                        try:
                            todoist_client.delete_task(task_id=task_id)
                            action_result = f"Task ID '{task_id}' deleted."
                        except Exception as e:
                            action_result = f"Error deleting task {task_id}: {str(e)}"
                else:
                    action_result = f"Error: Unknown function {function_name}."
                results.append(action_result)
            
            # For now, just join results. You might send these back to the LLM for a summary.
            return " ".join(results)

        elif response_message.content:
            return response_message.content
        else:
            return "No specific action taken or text response from LLM."

    except Exception as e:
        print(f"Critical error in handle_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Sorry, I encountered a critical error."
        