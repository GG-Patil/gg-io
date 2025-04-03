const API_URL = "http://127.0.0.1:5000"; // Flask server URL

// Fetch and display tasks
document.addEventListener("DOMContentLoaded", () => {
    fetchTasks();
});

async function fetchTasks() {
    try {
        let response = await fetch(`${API_URL}/get_tasks`);
        let tasks = await response.json();
        let taskList = document.getElementById("task_list");
        taskList.innerHTML = "";
        tasks.forEach(task => {
            let li = document.createElement("li");
            li.innerHTML = `${task.name}: ${task.description} 
                <button onclick="deleteTask(${task.id})">Delete</button>`;
            taskList.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching tasks:", error);
    }
}

async function createTask() {
    const taskName = document.getElementById("task_name").value;
    const taskDescription = document.getElementById("task_description").value;

    if (!taskName.trim()) {
        alert("Task name is required");
        return;
    }

    try {
        await fetch(`${API_URL}/create_task`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_name: taskName, description: taskDescription })
        });
        fetchTasks();
    } catch (error) {
        console.error("Error creating task:", error);
    }
}

async function deleteTask(taskId) {
    try {
        await fetch(`${API_URL}/delete_task`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId })
        });
        fetchTasks();
    } catch (error) {
        console.error("Error deleting task:", error);
    }
}
