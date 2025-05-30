<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/authStore';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// Form data
const email = ref('');
const emailError = ref('');
const password = ref('');
const passwordError = ref('');
const confirmPassword = ref('');
const confirmPasswordError = ref('');
const showPassword = ref(false);
const agreeToTerms = ref(false);

// Password validation
const passwordStrength = computed(() => {
  if (!password.value) return { score: 0, feedback: '' };

  const length = password.value.length;
  const hasUppercase = /[A-Z]/.test(password.value);
  const hasLowercase = /[a-z]/.test(password.value);
  const hasNumbers = /[0-9]/.test(password.value);
  const hasSpecial = /[^A-Za-z0-9]/.test(password.value);

  let score = 0;
  if (length >= 8) score += 1;
  if (length >= 12) score += 1;
  if (hasUppercase) score += 1;
  if (hasLowercase) score += 1;
  if (hasNumbers) score += 1;
  if (hasSpecial) score += 1;

  let feedback = '';
  if (score < 3) feedback = 'Weak password';
  else if (score < 5) feedback = 'Medium password';
  else feedback = 'Strong password';

  return { score, feedback };
});

// Password match validation
const passwordsMatch = computed(() => {
  if (!confirmPassword.value) return true;
  return password.value === confirmPassword.value;
});

// Handle registration submission
const handleRegister = async () => {
  // Form validation client side
  if (!email.value) {
    emailError.value = 'Email is required';
  }
  if (!password.value) {
    passwordError.value = 'Password is required';
  }
  if (!confirmPassword.value) {
    confirmPasswordError.value = 'Confirm password is required';
  }

  if (passwordStrength.value.score < 3) {
    passwordError.value = 'Please use a stronger password';
    return;
  }

  await authStore.register(email.value, password.value);
};

// Navigate to login page
const goToLogin = () => {
  router.push('/login');
};

// Navigate back to home
const goToHome = () => {
  router.push('/');
};
</script>

<template>
  <div class="register-container">
    <div class="register-card">
      <button class="back-button" @click="goToHome">
        ← Back to Home
      </button>
      <div class="card-header">
        <h1 class="title">
          Create your account
        </h1>
        <p class="subtitle">
          Join FocusTimer
        </p>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="your@email.com"
            required
            autocomplete="email">
          <div v-if="authStore.registerErrors.email" class="error-message">
            {{ authStore.registerErrors.email }}
          </div>
          <div v-if="emailError" class="error-message">
            {{ emailError }}
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <div class="password-input-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Create a strong password"
              required
              autocomplete="new-password">
            <button
              type="button"
              class="toggle-password"
              @click="showPassword = !showPassword">
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <div v-if="password" class="password-strength">
            <div class="strength-meter">
              <div
                class="strength-bar"
                :style="{ width: `${(passwordStrength.score / 6) * 100}%` }"
                :class="{
                  weak: passwordStrength.score < 3,
                  medium: passwordStrength.score >= 3 && passwordStrength.score < 5,
                  strong: passwordStrength.score >= 5
                }" />
            </div>
            <span class="strength-text">{{ passwordStrength.feedback }}</span>
          </div>
          <div v-if="authStore.registerErrors.password" class="error-message">
            {{ authStore.registerErrors.password }}
          </div>
          <div v-if="passwordError" class="error-message">
            {{ passwordError }}
          </div>
        </div>

        <div class="form-group">
          <label for="confirm-password">Confirm Password</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Confirm your password"
            required
            autocomplete="new-password">
          <div v-if="confirmPassword && !passwordsMatch" class="password-mismatch">
            Passwords do not match
          </div>
          <div v-if="authStore.registerErrors.confirm_password" class="error-message">
            {{ authStore.registerErrors.confirm_password }}
          </div>
          <div v-if="confirmPasswordError" class="error-message">
            {{ confirmPasswordError }}
          </div>
        </div>

        <div class="terms-agreement">
          <input
            id="agree-terms"
            v-model="agreeToTerms"
            type="checkbox"
            required>
          <label for="agree-terms">
            I agree to the <a href="#" class="terms-link">Terms of Service</a> and <a href="#" class="terms-link">Privacy Policy</a>
          </label>
        </div>

        <!-- For generic errors -->
        <div v-if="authStore.registerErrors.general" class="error-message">
          {{ authStore.registerErrors.general }}
        </div>

        <button
          type="submit"
          class="register-button"
          :disabled="authStore.isLoading">
          {{ authStore.isLoading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <div class="card-footer">
        <p>
          Already have an account? <button class="text-button" @click="goToLogin">
            Log in
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background-color: var(--color-background);
}

.register-card {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  width: 100%;
  max-width: 500px;
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

.register-form {
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
  transition: border-color 0.2s, box-shadow 0.2s;
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

.password-strength {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.strength-meter {
  height: 4px;
  background-color: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  transition: width 0.3s;
}

.strength-bar.weak {
  background-color: var(--color-error, #ef4444);
}

.strength-bar.medium {
  background-color: var(--color-warning, #f59e0b);
}

.strength-bar.strong {
  background-color: var(--color-success, #10b981);
}

.strength-text {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.password-mismatch {
  color: var(--color-error, #ef4444);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.terms-agreement {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.terms-link {
  color: var(--color-primary);
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

.error-message {
  font-size: 0.875rem;
  color: var(--color-error, #ef4444);
  padding: 0.75rem;
  border-radius: 0.375rem;
}

.register-button {
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

.register-button:hover {
  background-color: var(--color-primary-dark, #4338ca);
}

.register-button:disabled {
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
