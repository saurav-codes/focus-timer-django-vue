import { defineStore } from 'pinia';
import { useAuthStore } from './authStore';

export const useCalendarStore = defineStore('calendar', {
  state: () => ({
    isGoogleConnected: false,
    isLoading: false,
    events: [],
    error: null
  }),

  actions: {
    async checkGoogleConnection() {
      const authStore = useAuthStore();
      try {
        this.isLoading = true;
        const response = await authStore.axios_instance.get('api/gcalendar/status/');
        this.isGoogleConnected = response.data.connected;
        return this.isGoogleConnected;
      } catch (error) {
        console.error('Error checking Google connection:', error);
        this.isGoogleConnected = false;
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async startGoogleAuth() {
      const authStore = useAuthStore();
      try {
        this.isLoading = true;
        const response = await authStore.axios_instance.get('api/gcalendar/auth/start/');
        // Redirect to Google's authorization page
        window.location.href = response.data.auth_url;
      } catch (error) {
        console.error('Error starting Google auth:', error);
        this.error = 'Failed to connect to Google Calendar';
      } finally {
        this.isLoading = false;
      }
    },

    async fetchEvents(startStr, endStr) {
      const authStore = useAuthStore();
      try {
        this.isLoading = true;
        const response = await authStore.axios_instance.get(
          `api/gcalendar/events/?start=${startStr}&end=${endStr}`
        );
        this.events = response.data;
        return this.events;
      } catch (error) {
        console.error('Error fetching events:', error);
        this.error = 'Failed to fetch calendar events';
        return [];
      } finally {
        this.isLoading = false;
      }
    },

    async disconnectGoogleCalendar() {
      const authStore = useAuthStore();
      try {
        this.isLoading = true;
        await authStore.axios_instance.delete('api/gcalendar/disconnect/');
        this.isGoogleConnected = false;
        this.events = [];
        return true;
      } catch (error) {
        console.error('Error disconnecting Google Calendar:', error);
        this.error = 'Failed to disconnect Google Calendar';
        return false;
      } finally {
        this.isLoading = false;
      }
    }
  }
});
