<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import TaskColumn from "./TaskColumn.vue";
import CalendarHeader from "./CalendarHeader.vue";
import Sidebar from "./Sidebar.vue";

const columns = ref([
    {
        date: new Date(),
        tasks: [],
    },
]);

const apiBaseUrl = "http://localhost:8000";

const fetchTasks = async () => {
    try {
        const response = await axios.get(`${apiBaseUrl}/api/tasks/`);
        const tasks = response.data;

        // Reset tasks for the day
        if (columns.value[0]) {
            columns.value[0].tasks = tasks;
        }
    } catch (error) {
        console.error("Error fetching tasks:", error);
    }
};

const updateTaskStatus = async (task, newStatus) => {
    try {
        await axios.patch(`${apiBaseUrl}/api/tasks/${task.id}/`, {
            status: newStatus,
        });
    } catch (error) {
        console.error("Error updating task:", error);
    }
};

onMounted(() => {
    fetchTasks();
});
</script>

<template>
    <div class="app-container">
        <!-- <Sidebar /> -->

        <div class="main-content">
            <!-- <CalendarHeader /> -->

            <div class="calendar-view">
                <TaskColumn
                    v-for="column in columns"
                    :key="column.date"
                    :date="column.date"
                    :tasks="column.tasks"
                    @update-task="updateTaskStatus"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Updated overall layout styling for a bright, modern UI */

.app-container {
    display: flex;
    height: 100vh;
    background: #f2f3f5; /* Light background for the entire app */
    color: #333; /* Darker text for readability */
}

/* Sidebar styling might need additional updates in its own file */

.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.calendar-view {
    flex: 1;
    display: flex;
    overflow-x: auto;
    padding: 1rem;
    background: #f7f8fa;
    gap: 1rem;
}
</style>
