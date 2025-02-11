<script setup>
import TaskItem from "./TaskItem.vue";
import draggable from "vuedraggable";

const props = defineProps({
    date: {
        type: Date,
        required: true,
    },
    tasks: {
        type: Array,
        default: () => [],
    },
});

const emit = defineEmits(["update-task"]);

const formatDate = (date) => {
    return new Intl.DateTimeFormat("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
    }).format(date);
};
</script>

<template>
    <div class="task-column">
        <div class="column-header">
            <h2>{{ formatDate(date) }}</h2>
        </div>

        <div class="task-list">
            <draggable v-model="tasks" item-key="id">
                <template #item="{ element }">
                    <!-- <TaskItem
                        v-for="task in tasks"
                        :key="task.id"
                        :task="task"
                        @update="(status) => $emit('update-task', task, status)"
                    /> -->
                    <TaskItem
                        :task="element"
                        @update="(status) => $emit('update-task', element, status)"
                    />
                </template>
            </draggable>
        </div>
    </div>
</template>

<style scoped>
/* Updated styles for a modern, card-like UI similar to Sunsama */
.task-column {
    flex: 1;
    min-width: 300px;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden; /* Ensures inner elements follow round corners */
    margin: 1rem;
    display: flex;
    flex-direction: column;
}

.column-header {
    padding: 1rem;
    background-color: #f7f8fa;
    border-bottom: 1px solid #e1e4e8;
    text-align: center;
}

.column-header h2 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: #333333;
}

.task-list {
    flex: 1;
    padding: 1rem;
    background-color: #fafbfc;
    overflow-y: auto;
}
</style>
