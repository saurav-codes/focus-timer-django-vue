<script setup>
import { ref} from 'vue';
import { onClickOutside } from '@vueuse/core';
import { Plus, FolderIcon, LucideTrash } from 'lucide-vue-next';
import { useTaskStore } from '../stores/taskstore';
import { offset, flip, shift } from '@floating-ui/dom';
import { useFloating, autoUpdate} from '@floating-ui/vue';


const taskStore = useTaskStore();
const emit = defineEmits(["project-selected"]);

const isProjectPopupOpen = ref(false);
const projectButtonRef = ref(null);

// Set up floating UI for project popup
const projectPopupRef = ref(null);

const { floatingStyles: projectFloatingStyles } = useFloating(
  projectButtonRef,
  projectPopupRef,
  {
    whileElementsMounted: autoUpdate,  // keep the popup close to the button while screen size changes
    placement: 'bottom-start',
    middleware: [
      offset(8),
      flip(),
      shift()
    ]
  }
);


const newProjectTitle = ref('');
const isCreatingNew = ref(false);
// id to send to the backend
const selectedProjectId = ref(null);
// title to display in the button
const selectedProjectTitle = ref(null);

// close popup
const closePopup = () => {
  isProjectPopupOpen.value = false;
  isCreatingNew.value = false;
  newProjectTitle.value = '';
}

// Handle project selection
const selectProject = (projectId, projectTitle) => {
  selectedProjectId.value = projectId;
  selectedProjectTitle.value = projectTitle;
  emit('project-selected', projectId);
  closePopup();
};

// Toggle new project creation mode
const toggleNewProjectMode = () => {
  isCreatingNew.value = !isCreatingNew.value;
  if (isCreatingNew.value) {
    // Focus the input field after DOM update
    setTimeout(() => {
      document.getElementById('new-project-input')?.focus();
    }, 0);
  }
};

// Create and select a new project
const createAndSelectProject = async () => {
  if (newProjectTitle.value.trim()) {
    try {
      // Create the project in the backend
      const projectData = await taskStore.createProject({
        title: newProjectTitle.value.trim()
      });

      // Select the newly created project
      if (projectData) {
        selectProject(projectData.id, projectData.title);
      }

    } catch (error) {
      console.error('Failed to create project:', error);
    }
  }
};

// Handle cancel
const handleCancel = () => {
  isProjectPopupOpen.value = false;
  isCreatingNew.value = false;
  newProjectTitle.value = '';
};

// Handle clicking outside the popup
onClickOutside(projectPopupRef, () => {
  handleCancel();
});
</script>

<template>
  <!-- Project selector -->
  <button
    ref="projectButtonRef"
    class="option-button project-button"
    @click.stop="isProjectPopupOpen = !isProjectPopupOpen">
    <FolderIcon size="16" />
    <span>{{ selectedProjectTitle || 'No Project' }}</span>
  </button>

  <Teleport to="body">
    <div v-if="!!isProjectPopupOpen" ref="projectPopupRef" :style="projectFloatingStyles" class="project-dropdown-popup">
      <div class="popup-header">
        <span>Select Project</span>
      </div>

      <div class="popup-content">
        <!-- No project option -->
        <div
          class="project-option"
          :class="{ 'selected': selectedProjectTitle === null }"
          @click="selectProject(null)">
          <span>No Project</span>
        </div>

        <!-- Existing projects -->
        <div
          v-for="project in taskStore.projects"
          :key="project.id"
          class="project-option"
          :class="{ 'selected': selectedProjectId === project.id }"
          @click="selectProject(project.id, project.title)">
          <FolderIcon size="14" />
          <span class="project-content">{{ project.title }}
            <LucideTrash class="delete-button" size="14" @click.stop="taskStore.deleteProject(project.id)" />
          </span>
        </div>

        <!-- Create new project option -->
        <div v-if="!isCreatingNew" class="project-option new-project" @click="toggleNewProjectMode">
          <Plus size="14" />
          <span>Create New Project</span>
        </div>

        <!-- New project input field -->
        <div v-else class="new-project-input-container">
          <input
            id="new-project-input"
            v-model="newProjectTitle"
            type="text"
            placeholder="Project Name"
            @keydown.enter="createAndSelectProject">
          <div class="new-project-actions">
            <button class="btn-cancel" @click="toggleNewProjectMode">
              Cancel
            </button>
            <button
              class="btn-create"
              :disabled="!newProjectTitle.trim()"
              @click="createAndSelectProject">
              Create
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.project-dropdown-popup {
  position: fixed;
  width: 250px;
  background-color: var(--color-background);
  border-radius: 6px;
  box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05));
  z-index: 7;
  border: 1px solid var(--color-border);
}

.popup-header {
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.popup-content {
  max-height: 300px;
  overflow-y: auto;
}

.project-option {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.project-option:hover {
  background-color: var(--color-background-secondary);
}

.project-option.selected {
  background-color: var(--color-background-tertiary);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.project-option.new-project {
  border-top: 1px solid var(--color-border);
  color: var(--color-primary);
}

.project-option .project-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.project-content .delete-button {
  cursor: pointer;
  color: var(--color-error);
  transition: color 0.5s;
  background-color: transparent;
  padding: 0.15rem;
}

.delete-button:hover {
  background-color: var(--color-background-secondary);
  border: 1px solid var(--color-border);
}

.new-project-input-container {
  padding: 8px 12px;
  border-top: 1px solid var(--color-border);
}

.new-project-input-container input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-sm);
  margin-bottom: 8px;
  background-color: var(--color-input-background, var(--color-background-secondary));
  color: var(--color-text-primary);
}

.new-project-input-container input:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 0 2px var(--color-primary-light, rgba(147, 51, 234, 0.1));
}

.new-project-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-cancel, .btn-create {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background-color: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.btn-cancel:hover {
  background-color: var(--color-background-secondary);
}

.btn-create {
  background-color: var(--color-primary);
  border: 1px solid var(--color-primary);
  color: white;
}

.btn-create:hover {
  background-color: var(--color-primary-dark, #7e22ce);
}

.btn-create:disabled {
  background-color: var(--color-background-tertiary);
  border-color: var(--color-border);
  color: var(--color-text-tertiary);
  cursor: not-allowed;
}

.project-button {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.option-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background-color: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.option-button:hover {
  background-color: var(--color-background-tertiary);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

</style>
