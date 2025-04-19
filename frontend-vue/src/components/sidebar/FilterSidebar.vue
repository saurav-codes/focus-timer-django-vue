<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { XIcon, SearchIcon } from 'lucide-vue-next';
import { useTaskStore } from '../../stores/taskstore';
import { useUIStore } from '../../stores/uiStore';

const taskStore = useTaskStore();
const uiStore = useUIStore();

const searchQuery = ref('');
const selectedProjectId = ref(null);
const selectedTags = ref([]);

// Computed property to check if sidebar is visible
const isVisible = computed(() => uiStore.isFilterSidebarVisible);

// Watch for changes in sidebar visibility and fetch data when it becomes visible
watch(isVisible, async (newValue) => {
  if (newValue === true) {
    // Fetch data when sidebar is opened
    await loadFilterData();
  }
}, { immediate: false });

// Function to load filter data
const loadFilterData = async () => {
  try {
    await Promise.all([
      taskStore.fetchProjects(),
      taskStore.fetchTags()
    ]);
  } catch (error) {
    console.error('Error loading filter data:', error);
  }
};

// Function to close the sidebar
const closeSidebar = () => {
  uiStore.toggleFilterSidebar();
};

// Function to filter tasks by project
const selectProject = (projectId) => {
  if (selectedProjectId.value === projectId) {
    selectedProjectId.value = null;
    taskStore.setSelectedProjects([]);
  } else {
    selectedProjectId.value = projectId;
    taskStore.setSelectedProjects([projectId]);
  }
};

// Function to toggle tag selection
const toggleTag = (tagName) => {
  const index = selectedTags.value.indexOf(tagName);
  if (index === -1) {
    selectedTags.value.push(tagName);
  } else {
    selectedTags.value.splice(index, 1);
  }
  taskStore.setSelectedTags(selectedTags.value);
};

// Function to clear all filters
const clearFilters = () => {
  selectedProjectId.value = null;
  selectedTags.value = [];
  taskStore.clearFilters();
};

// Function to select all filters
const selectAll = () => {
  // Select all projects (since UI only allows single project selection, select the first one)
  if (filteredProjects.value.length > 0) {
    const firstProject = filteredProjects.value[0];
    selectedProjectId.value = firstProject.id;
    taskStore.setSelectedProjects([firstProject.id]);
  }

  // Select all tags
  const tagNames = filteredTags.value.map(tag => tag.name);
  selectedTags.value = tagNames;
  taskStore.setSelectedTags(tagNames);
};

// Computed properties for filtered lists
const filteredProjects = computed(() => {
  if (!searchQuery.value) return taskStore.projects;
  return taskStore.projects.filter(project =>
    project.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const filteredTags = computed(() => {
  if (!searchQuery.value) return taskStore.tags;
  return taskStore.tags.filter(tag =>
    tag.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Load projects and tags on component mount
onMounted(async () => {
  // Only load data initially if the sidebar is already visible
  if (isVisible.value) {
    await loadFilterData();
  }
});
</script>

<template>
  <div v-if="isVisible" class="filter-sidebar-overlay" @click="closeSidebar">
    <div class="filter-sidebar" @click.stop>
      <div class="filter-header">
        <h2>Apply filters</h2>
        <button class="close-btn" @click="closeSidebar">
          <XIcon size="20" />
        </button>
      </div>
      <p class="filter-description">
        Filter task data by projects and tags.
      </p>

      <!-- Search input -->
      <div class="search-container">
        <SearchIcon size="18" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search for label"
          class="search-input">
      </div>

      <!-- Projects section -->
      <div class="filter-section">
        <h3>Projects</h3>
        <div class="filter-items">
          <div
            v-for="project in filteredProjects"
            :key="project.id"
            class="filter-item"
            :class="{ 'selected': selectedProjectId === project.id }"
            @click="selectProject(project.id)">
            <div class="checkbox-wrapper">
              <input
                type="checkbox"
                :checked="selectedProjectId === project.id"
                @click.stop>
              <span class="checkmark" />
            </div>
            <span>{{ project.title }}</span>
          </div>
        </div>
      </div>

      <!-- Tags section -->
      <div class="filter-section">
        <h3>Tags</h3>
        <div class="filter-items">
          <div
            v-for="tag in filteredTags"
            :key="tag.id"
            class="filter-item"
            :class="{ 'selected': selectedTags.includes(tag.name) }"
            @click="toggleTag(tag.name)">
            <div class="checkbox-wrapper">
              <input
                type="checkbox"
                :checked="selectedTags.includes(tag.name)"
                @click.stop>
              <span class="checkmark" />
            </div>
            <span>{{ tag.name }}</span>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="filter-actions">
        <button class="clear-btn" @click="clearFilters">
          Clear all
        </button>
        <button class="select-all-btn" @click="selectAll">
          Select all
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
}

.filter-sidebar {
  width: 320px;
  height: 95vh;
  background-color: var(--color-background);
  box-shadow: var(--shadow-lg);
  padding: 1.5rem;
  overflow-y: scroll;
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  0% { transform: translateX(100%); }
  100% { transform: translateX(0); }
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.filter-header h2 {
  font-size: 1.5rem;
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: var(--color-background-tertiary);
  color: var(--color-text-secondary);
}

.filter-description {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
  margin-bottom: 1.5rem;
}

.search-container {
  position: relative;
  margin-bottom: 1.5rem;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-tertiary);
}

.search-input {
  width: 100%;
  padding: 0.75rem 0.75rem 0.75rem 2.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.filter-section {
  margin-bottom: 1.5rem;
}

.filter-section h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.filter-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-item {
  display: flex;
  align-items: center;
  padding: 0.625rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.filter-item:hover {
  background-color: var(--color-background-tertiary);
}

.filter-item.selected {
  background-color: rgba(var(--color-primary-rgb), 0.1);
}

.checkbox-wrapper {
  position: relative;
  margin-right: 0.75rem;
  min-width: 20px;
  height: 20px;
}

.checkbox-wrapper input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: var(--color-background-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 3px;
}

.filter-item.selected .checkmark {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.filter-item.selected .checkmark:after {
  content: "";
  position: absolute;
  display: block;
  left: 7px;
  top: 3px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.clear-btn {
  padding: 0.625rem 1.25rem;
  background-color: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  transition: all 0.2s;
}

.clear-btn:hover {
  background-color: var(--color-background-tertiary);
  border-color: var(--color-text-tertiary);
}

.select-all-btn {
  padding: 0.625rem 1.25rem;
  background-color: var(--color-primary);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: white;
  font-weight: var(--font-weight-medium);
  transition: all 0.2s;
}

.select-all-btn:hover {
  background-color: var(--color-primary-dark);
}
</style>
