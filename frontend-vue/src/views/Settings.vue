<script setup>
import { useAuthStore } from '../stores/authStore';
import { onMounted, ref } from 'vue';

const authStore = useAuthStore();
const userData = ref({});

onMounted(() => {
  authStore.fetchUserData().then((data) => {
    userData.value = data;
  });
});
</script>

<template>
  <div>
    <main>
      <h2>settings will be here</h2>
      <code>{{ userData }}</code>
      <button @click="authStore.logout">logout</button>
    </main>
  </div>
</template>
