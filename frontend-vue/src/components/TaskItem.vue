<script setup>
const props = defineProps({
    task: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(["update"]);

const getTimeString = (task) => {
    // TODO: Implement time formatting
    return "9:30 AM";
};
</script>

<template>
    <div class="task-item">
        <div class="task-time">{{ getTimeString(task) }}</div>
        <div class="task-content">
            <div class="task-title">{{ task.title }}</div>
            <div class="task-description">{{ task.description }}</div>
        </div>
        <div class="task-status">
            <div class="status-dot" :class="task.status" />
        </div>
    </div>
</template>

<style scoped>
.task-item {
    display: flex;
    align-items: flex-start;
    padding: 0.75rem;
    background: #262626;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.task-time {
    font-size: 0.8rem;
    color: #888;
    width: 70px;
}

.task-content {
    flex: 1;
    margin: 0 0.5rem;
}

.task-title {
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.task-description {
    font-size: 0.9rem;
    color: #888;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #666;
}

.status-dot.done {
    background: #4caf50;
}

.status-dot.in_progress {
    background: #2196f3;
}

.status-dot.todo {
    background: #ffc107;
}
</style>
