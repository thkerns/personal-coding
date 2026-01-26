#Daily Task Manager
import datetime
import json
import os
#------------------------------------------------------------------------------
# File to store tasks
TASKS_FILE = 'tasks.json'
#------------------------------------------------------------------------------
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return {}
#------------------------------------------------------------------------------
def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)
#------------------------------------------------------------------------------
def get_today():
    return datetime.date.today().isoformat()
#------------------------------------------------------------------------------
def display_tasks(tasks, date):
    print(f"\nTasks for {date}:")
    if date not in tasks or not tasks[date]:
        print("No tasks.")
        return
    for i, task in enumerate(tasks[date], 1):
        status = task.get('status', 'pending')
        if status == 'completed':
            symbol = "[✓]"
        elif status == 'failed':
            symbol = "[X]"
        else:
            symbol = "[ ]"
        print(f"{i}. {symbol} {task['description']}")
#------------------------------------------------------------------------------
def add_task(tasks, date, description):
    if not description or description.lower() == 'cancel':
        print("Cancelled.")
        return
    if date not in tasks:
        tasks[date] = []
    tasks[date].append({'description': description, 'status': 'pending'})
    save_tasks(tasks)
    print(f"Task added: {description}")
#------------------------------------------------------------------------------
def mark_complete(tasks, date, index):
    if index == -1:
        print("Cancelled.")
        return
    if date in tasks and 0 <= index < len(tasks[date]):
        tasks[date][index]['status'] = 'completed'
        save_tasks(tasks)
        print("Task marked as complete.")
    else:
        print("Invalid task index.")
#------------------------------------------------------------------------------
def mark_incomplete(tasks, date, index):
    if index == -1:
        print("Cancelled.")
        return
    if date in tasks and 0 <= index < len(tasks[date]):
        tasks[date][index]['status'] = 'pending'
        save_tasks(tasks)
        print("Task marked as incomplete.")
    else:
        print("Invalid task index.")
#------------------------------------------------------------------------------
def mark_failed(tasks, date, index):
    if index == -1:
        print("Cancelled.")
        return
    if date in tasks and 0 <= index < len(tasks[date]):
        tasks[date][index]['status'] = 'failed'
        save_tasks(tasks)
        print("Task marked as failed.")
    else:
        print("Invalid task index.")
#------------------------------------------------------------------------------
def remove_task(tasks, date, index):
    if index == -1:
        print("Cancelled.")
        return
    if date in tasks and 0 <= index < len(tasks[date]):
        removed_task = tasks[date].pop(index)
        save_tasks(tasks)
        print(f"Task removed: {removed_task['description']}")
    else:
        print("Invalid task index.")
#------------------------------------------------------------------------------
def main():
    tasks = load_tasks()
    today = get_today()
    
    while True:
        print(f"\nCurrent Date: {today}")
        display_tasks(tasks, today)
        
        print("\nOptions:")
        print("1. Add a task")
        print("2. Mark a task as complete")
        print("3. Mark a task as incomplete")
        print("4. Mark a task as failed")
        print("5. Remove a task")
        print("6. View tasks for another date")
        print("7. Exit")
        
        choice = input("Choose an option (or 0 to exit): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            desc = input("Enter task description (or 'cancel' to go back): ").strip()
            add_task(tasks, today, desc)
        elif choice == '2':
            try:
                index = int(input("Enter task number to mark complete (or 0 to cancel): ")) - 1
                mark_complete(tasks, today, index)
            except ValueError:
                print("Invalid input. Returning to menu.")
        elif choice == '3':
            try:
                index = int(input("Enter task number to mark incomplete (or 0 to cancel): ")) - 1
                mark_incomplete(tasks, today, index)
            except ValueError:
                print("Invalid input. Returning to menu.")
        elif choice == '4':
            try:
                index = int(input("Enter task number to mark failed (or 0 to cancel): ")) - 1
                mark_failed(tasks, today, index)
            except ValueError:
                print("Invalid input. Returning to menu.")
        elif choice == '5':
            try:
                index = int(input("Enter task number to remove (or 0 to cancel): ")) - 1
                remove_task(tasks, today, index)
            except ValueError:
                print("Invalid input. Returning to menu.")
        elif choice == '6':
            date = input("Enter date (YYYY-MM-DD) (or 'cancel' to go back): ").strip()
            if not date or date.lower() == 'cancel':
                print("Cancelled.")
            else:
                display_tasks(tasks, date)
        elif choice == '7':
            break
        else:
            print("Invalid choice.")
#------------------------------------------------------------------------------
if __name__ == "__main__":
    main()