import { defineStore } from 'pinia';
import axios from 'axios';
import router from '../router';
import { useLocalStorage } from '@vueuse/core';

const userDataLocalStorage = useLocalStorage('userData', {});
const isAuthenticatedLocalStorage = useLocalStorage('isAuthenticated', false);
// const BACKEND_BASE_URL = 'http://localhost:8000/'
const BACKEND_BASE_URL = 'http://tymr.online/'

// setting this to allow cookies to be set by
// backend using response headers
// this is also required for session authentication to work
const axios_instance = axios.create({
  baseURL: BACKEND_BASE_URL,
  withCredentials: true,
  withXSRFToken: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

function parseErrors(errorData, error_target, error_target_name) {
  if (error_target_name === 'login') {
    error_target["general"] = errorData.message;
  }
  if (errorData.error && typeof errorData.error === 'string' && errorData.error.startsWith('{"')) {
    try {
      const parsedErrors = JSON.parse(errorData.error);
      Object.entries(parsedErrors).forEach(([field, fieldErrors]) => {
        if (Array.isArray(fieldErrors)) {
          error_target[field] = fieldErrors[0].message || fieldErrors[0];
        } else {
          error_target[field] = fieldErrors;
        }
      });
    } catch (e) {
      console.error('Error parsing registration errors:', e);
      error_target.general = errorData.error;
    }
  } else {
    // Process direct error objects
    Object.entries(errorData).forEach(([field, fieldErrors]) => {
      if (Array.isArray(fieldErrors)) {
        error_target[field] = fieldErrors.join(', ');
      } else {
        error_target[field] = fieldErrors;
      }
    });
  }
}


export const useAuthStore = defineStore('authStore', {
  state: () => ({
    isLoading: false,
    registerErrors: {},
    loginErrors: {},
    userData: userDataLocalStorage,
    isAuthenticated: isAuthenticatedLocalStorage,
  }),

  getters: {
    axios_instance: () => axios_instance,
  },

  actions: {
    setupInterceptors() {
      // Set up axios interceptor for handling 401 errors
      axios_instance.interceptors.response.use(
        response => response,
        error => {
          // Check if error is 401 Unauthorized
          if (error.response && error.response.status === 403) {
            // Logout if the user is authenticated
            if (this.isAuthenticated) {
              console.log('Token expired or invalid, logging out...');
              this.logout();
            }
          }
          return Promise.reject(error);
        }
      );
    },

    async login(email, password) {
      this.isLoading = true;

      try {
        await axios_instance.post('auth/login/', {
          email,
          password
        });

        router.push('/kanban-planner');
        this.isAuthenticated = true;
        this.userData = await this.fetchUserData();
        return true;
      } catch (error) {
        console.error('Login error:', error);
        parseErrors(error.response?.data, this.loginErrors, 'login');
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async setCSRFToken() {
      // Set the CSRF token
      await axios_instance.get('auth/set-csrf-token/');
      console.log('CSRF token set');
    },

    async register(email, password) {
      this.isLoading = true;
      try {
        await axios_instance.post('auth/register/', {
          email,
          password
        });
        return await this.login(email, password);
      } catch (error) {
        console.error('Registration error:', error);
        // Clear existing errors
        this.registerErrors = {};

        // Process errors by field
        const errorData = error.response?.data || {};

        // If we have an 'error' key with JSON string
        parseErrors(errorData, this.registerErrors, 'register');
      } finally {
        this.isLoading = false;
      }
      return false;
    },

    async fetchUserData() {
      try {
        const response = await axios_instance.get('auth/user/');
        return response.data;
      } catch (error) {
        console.error('Error fetching user data:', error);
        return null;
      }
    },

    async logout() {
      try {
        await axios_instance.post('auth/logout/');
        console.log('Logged out successfully');
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        // Clear auth data regardless of API call success/failure
        this.isAuthenticated = false;
        // Redirect to home page
        router.push('/');
      }
    },

    // Initialize auth state, to be called when app starts
    initAuth() {
      // Set up interceptors
      this.setupInterceptors();
      this.setCSRFToken();
    },
  }
});
