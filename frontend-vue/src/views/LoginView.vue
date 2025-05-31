<script setup>
  import { ref } from 'vue'
  import { useAuthStore } from '../stores/authStore'
  import { useRouter } from 'vue-router'

  const authStore = useAuthStore()
  const router = useRouter()

  // Form data
  const email = ref('')
  const password = ref('')
  const showPassword = ref(false)

  // Error handling
  const formError = ref('')

  // Handle login submission
  const handleLogin = async () => {
    if (!email.value || !password.value) {
      formError.value = 'Please enter both email and password'
      return
    }

    formError.value = ''
    await authStore.login(email.value, password.value)
  }

  // Navigate to register page
  const goToRegister = () => {
    router.push('/register')
  }

  // Navigate back to home
  const goToHome = () => {
    router.push('/')
  }
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <button class="back-button" @click="goToHome">← Back to Home</button>
      <div class="card-header">
        <h1 class="title">Log in to Tymr Online</h1>
        <p class="subtitle">Enter your credentials to access your account</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" placeholder="your@email.com" required autocomplete="email" />
        </div>
        <div v-if="authStore.loginErrors.email" class="error-message">
          {{ authStore.loginErrors.email }}
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <div class="password-input-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Enter your password"
              required
              autocomplete="current-password" />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <div v-if="authStore.loginErrors.password" class="error-message">
            {{ authStore.loginErrors.password }}
          </div>
        </div>

        <div class="form-options">
          <a href="#" class="forgot-password">Forgot password?</a>
        </div>

        <div v-if="formError || authStore.loginErrors.general" class="error-message">
          {{ formError || authStore.loginErrors.general }}
        </div>

        <button type="submit" class="login-button" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? 'Logging in...' : 'Log In' }}
        </button>
      </form>

      <div class="card-footer">
        <p>Don't have an account? <button class="text-button" @click="goToRegister">Sign up</button></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .login-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    background-color: var(--color-background);
  }

  .login-card {
    background-color: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    width: 100%;
    max-width: 450px;
    padding: 2rem;
    box-shadow: var(--shadow-md);
  }

  .card-header {
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
  }

  .back-button {
    position: absolute;
    background: none;
    border: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    transition: color 0.2s;
  }

  .back-button:hover {
    color: var(--color-primary);
  }

  .title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
  }

  .subtitle {
    color: var(--color-text-tertiary);
    font-size: 0.95rem;
  }

  .login-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  .form-group input {
    padding: 0.75rem;
    border-radius: 0.375rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-input-background);
    color: var(--color-text-primary);
    font-size: 1rem;
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
  }

  .form-group input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-light, rgba(99, 102, 241, 0.2));
  }

  .password-input-wrapper {
    position: relative;
  }

  .toggle-password {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    font-size: 0.875rem;
  }

  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
  }

  .forgot-password {
    color: var(--color-primary);
    text-decoration: none;
  }

  .error-message {
    font-size: 0.875rem;
    color: var(--color-error, #ef4444);
    padding: 0.75rem;
    border-radius: 0.375rem;
  }

  .login-button {
    padding: 0.75rem;
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .login-button:hover {
    background-color: var(--color-primary-dark, #4338ca);
  }

  .login-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .card-footer {
    margin-top: 2rem;
    text-align: center;
    color: var(--color-text-tertiary);
    font-size: 0.95rem;
  }

  .text-button {
    background: none;
    border: none;
    color: var(--color-primary);
    cursor: pointer;
    font-size: inherit;
    font-weight: 500;
  }

  .text-button:hover {
    text-decoration: underline;
  }
</style>
