const API_URL = "http://127.0.0.1:5000"; // Adjust based on your Flask server URL

// Fetch and display tasks
function fetchTasks() {
    fetch(`${API_URL}/get_tasks`)
        .then(response => response.json())
        .then(tasks => {
            let taskList = document.getElementById("task_list");
            taskList.innerHTML = ""; // Clear the list
            tasks.forEach(task => {
                let li = document.createElement("li");
                li.innerHTML = `${task.name}: ${task.description} <button onclick="deleteTask(${task.id})">Delete</button>`;
                taskList.appendChild(li);
            });
        })
        .catch(error => console.error("Error fetching tasks:", error));
}

// Create a new task
function createTask() {
    const taskName = document.getElementById("task_name").value;
    const taskDescription = document.getElementById("task_description").value;

    fetch(`${API_URL}/create_task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_name: taskName, description: taskDescription })
    })
    .then(response => response.json())
    .then(() => fetchTasks()) // Refresh tasks list
    .catch(error => console.error("Error creating task:", error));
}

// Delete a task
function deleteTask(taskId) {
    fetch(`${API_URL}/delete_task`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: taskId })
    })
    .then(response => response.json())
    .then(() => fetchTasks()) // Refresh tasks list
    .catch(error => console.error("Error deleting task:", error));
}

// Load tasks when the page loads
document.addEventListener("DOMContentLoaded", fetchTasks);
