<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useAuthStore } from '../stores/authStore'
import { LogOut, LucidePencil } from 'lucide-vue-next'

const authStore = useAuthStore()

// Build a list of time zones (modern browsers support Intl.supportedValuesOf)
const timeZones = Intl.supportedValuesOf
  ? Intl.supportedValuesOf('timeZone')
  : ['UTC']

// Initialize selectedTimezone from the stored userData or fallback to browser locale
const selectedTimezone = ref(
  authStore.userData?.timezone ||
    Intl.DateTimeFormat().resolvedOptions().timeZone
)

// Auto-save when timezone selection changes
watch(selectedTimezone, (newTz, oldTz) => {
  if (newTz && newTz !== authStore.userData?.timezone) {
    saveTimezone()
  }
})

// Persist the updated timezone
async function saveTimezone() {
  try {
    await authStore.updateUserTimezone(selectedTimezone.value)
    // Optionally show a success message or toast here
    console.log('Timezone updated to', selectedTimezone.value)
  } catch (err) {
    console.error('Failed to update timezone', err)
  }
}

// Reactive clock in user's timezone
const now = ref(new Date())
let timerId = null
onMounted(() => {
  timerId = setInterval(() => {
    now.value = new Date()
  }, 1000)
})
onUnmounted(() => {
  clearInterval(timerId)
})

const localizedTime = computed(() => {
  try {
    return Intl.DateTimeFormat(undefined, {
      timeZone: selectedTimezone.value,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    }).format(now.value)
  } catch {
    return now.value.toUTCString()
  }
})
// Suggested timezone based on browser
const suggestedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone

// Apply the suggested timezone and trigger save
function applySuggestedTimezone() {
  selectedTimezone.value = suggestedTimezone
  saveTimezone()
}

// Editable full name state and save action
const fullName = ref(authStore.userData.full_name || '')

const inputEditable = ref(false)
const fullnameinputbox = ref(null)

onClickOutside(fullnameinputbox, ()=> {
  inputEditable.value = false
})

async function saveProfile() {
  try {
    await authStore.updateUserProfile(fullName.value)
    console.log('Profile updated to', fullName.value)
  } catch (err) {
    console.error('Failed to update profile', err)
  } finally {
    inputEditable.value = false
  }
}

</script>

<template>
  <div class="settings-container">
    <main class="settings-main">
      <h2>Settings</h2>
      <!-- User profile details -->
      <div class="profile-info">
        <div class="profile-row">
          <span class="label">Email:</span>
          <span class="value">{{ authStore.userData.email }}</span>
        </div>
        <div class="profile-row">
          <span class="label">Full Name:</span>
          <div class="edit-field">
            <input
              v-if="inputEditable"
              ref="fullnameinputbox"
              v-model="fullName"
              class="full-name-input"
              @blur="saveProfile">
            <span v-else class="value" @click="inputEditable=true">{{ fullName }}</span>
            <LucidePencil v-if="!inputEditable" :size="16" class="edit-icon" @click="inputEditable = true" />
          </div>
        </div>
      </div>
      <div class="current-time">
        <label>Local Time ({{ selectedTimezone }}):</label>
        <span>{{ localizedTime }}</span>
      </div>

      <div class="form-group">
        <label for="timezone-select">Timezone</label>
        <select
          id="timezone-select"
          v-model="selectedTimezone"
          class="timezone-select">
          <option v-for="tz in timeZones" :key="tz" :value="tz">
            {{ tz }}
          </option>
        </select>
      </div>

      <!-- Subheadline suggesting browser timezone -->
      <div v-if="selectedTimezone !== suggestedTimezone" class="timezone-suggestion">
        <small>
          Suggested:
          <span
            class="suggested-link"
            @click="applySuggestedTimezone">{{ suggestedTimezone }}</span>
        </small>
      </div>

      <!-- Timezone now auto-saves on change; Save button removed -->

      <button class="logout-button" @click="authStore.logout">
        <LogOut size="16" />
        <span>Logout</span>
      </button>
    </main>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 2rem;
}

.settings-main {
  max-width: 400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.timezone-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 1rem;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background-color var(--transition-base), color var(--transition-base);
}
.logout-button:hover {
  background-color: var(--color-background-tertiary);
  color: var(--color-text-primary);
}

.suggested-link {
  cursor: pointer;
}

/* New edit-field & icon styling */
.edit-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.edit-icon {
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: color var(--transition-base);
}
.edit-icon:hover {
  color: var(--color-primary);
}

.profile-info {
  padding: 1rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
}
.profile-info .profile-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.profile-info .label {
  font-weight: 500;
}
.profile-info .value {
  color: var(--color-text-secondary);
}
.full-name-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
  font-size: 1rem;
  transition: border-color var(--transition-base);
}
.full-name-input:focus {
  outline: none;
  border-color: var(--color-primary);
}
</style>
