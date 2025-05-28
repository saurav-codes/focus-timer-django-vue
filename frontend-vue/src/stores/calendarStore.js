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
        // Set error message with details if available
        this.error = error.response?.data?.error || "Error checking Google connection";
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
        // Handle auth error with specific details if available
        this.error = error.response?.data?.error || 'Failed to connect to Google Calendar';
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
        // Update error state with specific details if available
        this.error = error.response?.data?.error || 'Failed to fetch calendar events';
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
        // Update error state with specific details if available
        this.error = error.response?.data?.error || 'Failed to disconnect Google Calendar';
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    async updateGoogleCalendarEvent(eventId, updateData) {
      const authStore = useAuthStore();
      try {
        this.isLoading = true;
        // Ensure the updateData contains all required fields in the correct format
        // The API expects specific format for updating Google Calendar events

        // Make the API call to update the event
        await authStore.axios_instance.put(`api/gcalendar/events/${eventId}/`, updateData);
        return true;
      } catch (error) {
        // Handle error and provide feedback
        if (error.response && error.response.data) {
          this.error = error.response.data.error || 'Failed to update Google Calendar event';
        } else {
          this.error = 'Network error while updating event';
        }
        return false;
      } finally {
        this.isLoading = false;
      }
    }
  }
});
