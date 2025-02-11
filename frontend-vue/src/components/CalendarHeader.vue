<script setup>
import { ref } from 'vue'

const currentDate = ref(new Date())

const formatMonth = (date) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric'
  }).format(date)
}

const navigateMonth = (direction) => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(newDate.getMonth() + direction)
  currentDate.value = newDate
}
</script>

<template>
  <header class="calendar-header">
    <div class="header-left">
      <button @click="navigateMonth(-1)" class="nav-btn">&lt;</button>
      <h2>{{ formatMonth(currentDate) }}</h2>
      <button @click="navigateMonth(1)" class="nav-btn">&gt;</button>
    </div>
    <div class="header-right">
      <button class="today-btn">Today</button>
    </div>
  </header>
</template>

<style scoped>
.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #1e1e1e;
  border-bottom: 1px solid #333;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.nav-btn {
  background: transparent;
  border: 1px solid #444;
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.nav-btn:hover {
  background: #333;
}

.today-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.today-btn:hover {
  background: #1976D2;
}
</style> 