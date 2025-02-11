<script setup>
const channels = [
  { id: 1, name: 'Personal', color: '#4CAF50' },
  { id: 2, name: 'Work', color: '#2196F3' },
  { id: 3, name: 'Projects', color: '#FFC107' }
]

const calendars = [
  { id: 1, name: 'My Calendar', color: '#E91E63' },
  { id: 2, name: 'Team Calendar', color: '#9C27B0' }
]
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-section">
      <h3>Channels</h3>
      <ul class="sidebar-list">
        <li v-for="channel in channels" :key="channel.id" class="sidebar-item">
          <span class="color-dot" :style="{ background: channel.color }"></span>
          {{ channel.name }}
        </li>
      </ul>
    </div>

    <div class="sidebar-section">
      <h3>Calendars</h3>
      <ul class="sidebar-list">
        <li v-for="calendar in calendars" :key="calendar.id" class="sidebar-item">
          <span class="color-dot" :style="{ background: calendar.color }"></span>
          {{ calendar.name }}
        </li>
      </ul>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  background: #1e1e1e;
  border-right: 1px solid #333;
  padding: 1rem;
}

.sidebar-section {
  margin-bottom: 2rem;
}

h3 {
  color: #888;
  font-size: 0.9rem;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  margin-bottom: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
}

.sidebar-item:hover {
  background: #333;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 0.75rem;
}
</style> 