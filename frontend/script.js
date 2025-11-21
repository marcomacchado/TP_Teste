const baseUrl = "http://127.0.0.1:5000/tasks/";
const CATEGORIES = ["Trabalho", "Pessoal", "Casa", "Saúde", "Finanças"];

async function fetchTasks() {
    const pendingTasksContainer = document.getElementById("pending-tasks");
    const completedTasksContainer = document.getElementById("completed-tasks");

    pendingTasksContainer.innerHTML = "";
    completedTasksContainer.innerHTML = "";

    try {
        const response = await fetch(baseUrl);
        const tasks = await response.json();

        tasks.forEach(task => {
            const taskElement = document.createElement("li");
            taskElement.innerText = `${task.description} - ${task.category} - Prazo: ${task.deadline}`;

            const completeButton = document.createElement("button");
            completeButton.textContent = "Concluir";
            completeButton.addEventListener("click", () => markTaskCompleted(task.id));

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Deletar";
            deleteButton.addEventListener("click", () => deleteTask(task.id));

            taskElement.appendChild(completeButton);
            taskElement.appendChild(deleteButton);

            if (task.completed) {
                taskElement.classList.add("completed");
                completedTasksContainer.appendChild(taskElement);
            } else {
                pendingTasksContainer.appendChild(taskElement);
            }
        });
    } catch (error) {
        console.error("Erro ao buscar tarefas:", error);
    }
}

async function addTask(description, category, deadline) {
    await fetch(baseUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, category, deadline }),
    });

    fetchTasks();
}

async function markTaskCompleted(taskId) {
    await fetch(`${baseUrl}${taskId}/complete`, { method: "PATCH" });
    fetchTasks();
}

async function deleteTask(taskId) {
    await fetch(`${baseUrl}${taskId}`, { method: "DELETE" });
    fetchTasks();
}

document.getElementById("task-form").addEventListener("submit", event => {
    event.preventDefault();

    const description = document.getElementById("description").value;
    const category = document.getElementById("category").value;
    const deadline = document.getElementById("deadline").value;

    addTask(description, category, deadline);
    document.getElementById("task-form").reset();
});

const toggleThemeButton = document.getElementById('toggle-theme');
const body = document.body;

// Função para alternar entre temas claro e escuro
toggleThemeButton.addEventListener('click', () => {
    body.classList.toggle('dark-mode');

    if (body.classList.contains('dark-mode')) {
        toggleThemeButton.textContent = '☀️'; // Modo Claro
    } else {
        toggleThemeButton.textContent = '🌙'; // Modo Escuro
    }
});

fetchTasks();
