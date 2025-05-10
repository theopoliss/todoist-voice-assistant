import json
from openai import AsyncOpenAI
from .config import settings
from app import todoist_client # Import your Todoist functions
import re # Moved import re to top level

# Initialize AsyncOpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)

# --- Helper to parse priority ---
def parse_priority(priority_str: str | None) -> int | None:
    if not priority_str:
        return None
    # Extract digits. "priority 1" -> "1", "p2" -> "2", "4" -> "4"
    match = re.search(r'\d+', priority_str)
    if match:
        num = int(match.group(0))
        if 1 <= num <= 4:
            return num
    return None # Or raise an error, or return a default

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
                    "priority": {
                        "type": "string",
                        "description": "The priority of the task from 1 to 4 (e.g. 'priority 1', 'p2', '3'). Optional."
                    }
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_todoist_tasks",
            "description": "Finds Todoist tasks based on a search query (keywords in task content). Use this to get a task_id if the user wants to update or delete a task but doesn't provide its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords to search for in the task content (e.g., 'English paper', 'milk').",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_todoist_task",
            "description": "Update an existing task in Todoist. If you don't have the task_id, use 'find_todoist_tasks' first to get it based on the task's content. Then call this function with the task_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to update. Get this using 'find_todoist_tasks' if not directly known.",
                    },
                    "content": {"type": "string", "description": "The new content for the task. Optional."},
                    "due_string": {"type": "string", "description": "The new due date for the task. Optional."},
                    "priority": {"type": "string", "description": "The new priority (1-4). Optional."}
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todoist_task",
            "description": "Delete a task from Todoist using its ID. If you don't have the task_id, use 'find_todoist_tasks' first to get it based on the task's content. Then call this function with the task_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to delete. Get this using 'find_todoist_tasks' if not directly known.",
                    },
                },
                "required": ["task_id"],
            },
        },
    }
]

async def handle_user(text: str) -> str:
    try:
        print(f"User input: {text}")
        messages = [{"role": "user", "content": text}] 

        while True: 
            completion = await client.chat.completions.create(
                model=settings.model,
                messages=messages, 
                tools=tools,
                tool_choice="auto",
            )

            response_message = completion.choices[0].message
            print(f"LLM response message: {response_message}")

            tool_calls = response_message.tool_calls
            # Fallback for older function_call attribute, ensuring it's added to messages correctly if present
            if not tool_calls and response_message.function_call:
                # Append the assistant's message that contains the function_call
                messages.append(response_message)
                tool_calls = [{
                    "id": "legacy_call_" + str(len(messages)), # Generate a unique enough ID
                    "type": "function", 
                    "function": response_message.function_call
                }]
            elif tool_calls: # If there are tool_calls, append the assistant's message
                 messages.append(response_message)
            else:
                # No tool calls, LLM intends to respond directly with text
                if response_message.content:
                    return response_message.content
                # If last message was a tool result, provide that as context if no direct content
                elif messages[-1]["role"] == "tool": 
                     return f"Action completed. Last tool message: {messages[-1]['content']}"
                return "LLM interaction finished without a direct text response or further tool calls."
            
            # At this point, tool_calls should be populated if we are to proceed with tool execution
            if not tool_calls: # Should ideally not be reached if logic above is correct, but as a safeguard
                break

            current_tool_results_for_llm = []
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args_json = tool_call.function.arguments
                try:
                    function_args = json.loads(function_args_json)
                except json.JSONDecodeError:
                    current_tool_results_for_llm.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": f"Error: Invalid JSON arguments: {function_args_json}"
                    })
                    continue

                print(f"LLM calling function: {function_name} with args: {function_args}")
                action_result_content = ""

                if function_name == "create_todoist_task":
                    content = function_args.get("content")
                    due_string = function_args.get("due_string")
                    priority_str = function_args.get("priority")
                    priority_int = parse_priority(priority_str)
                    if not content:
                        action_result_content = "Error: Task content is missing."
                    else:
                        try:
                            task = todoist_client.create_task(
                                content=content, 
                                due_string=due_string, 
                                priority=priority_int
                            )
                            action_result_content = f"Task '{content}' created successfully (ID: {task.id})."
                        except Exception as e:
                            action_result_content = f"Error creating task: {str(e)}"
                
                elif function_name == "find_todoist_tasks":
                    query = function_args.get("query")
                    if not query:
                        action_result_content = "Error: Search query is missing."
                    else:
                        try:
                            found_tasks = todoist_client.find_tasks(query=query)
                            if found_tasks:
                                action_result_content = f"Found tasks: {json.dumps(found_tasks)}"
                            else:
                                action_result_content = "No tasks found matching that query."
                        except Exception as e:
                            action_result_content = f"Error finding tasks: {str(e)}"

                elif function_name == "update_todoist_task":
                    task_id = function_args.get("task_id")
                    if not task_id:
                        action_result_content = "Error: Task ID is missing. Please use 'find_todoist_tasks' to get the task_id first."
                    else:
                        patch_args = {k: v for k, v in function_args.items() if k != 'task_id'}
                        if "priority" in patch_args and isinstance(patch_args["priority"], str):
                            patch_args["priority"] = parse_priority(patch_args["priority"])
                        if not patch_args:
                             action_result_content = "Error: No update parameters provided."
                        else:
                            try:
                                todoist_client.update_task(task_id=task_id, **patch_args)
                                action_result_content = f"Task ID '{task_id}' updated."
                            except Exception as e:
                                action_result_content = f"Error updating task {task_id}: {str(e)}"

                elif function_name == "delete_todoist_task":
                    task_id = function_args.get("task_id")
                    if not task_id:
                        action_result_content = "Error: Task ID is missing. Please use 'find_todoist_tasks' to get the task_id first."
                    else:
                        try:
                            todoist_client.delete_task(task_id=task_id)
                            action_result_content = f"Task ID '{task_id}' deleted."
                        except Exception as e:
                            action_result_content = f"Error deleting task {task_id}: {str(e)}"
                else:
                    action_result_content = f"Error: Unknown function {function_name}."

                current_tool_results_for_llm.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": action_result_content,
                })
            
            messages.extend(current_tool_results_for_llm)
            print(f"Sending tool results back to LLM: {current_tool_results_for_llm}")
            # Loop continues to make the next API call with updated messages

    except Exception as e:
        print(f"Critical error in handle_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Sorry, I encountered a critical error."
        