<template>
  <div id="app">
    <div class="container">
      <h1>{{ title }}</h1>
      <p>{{ message }}</p>
      <button @click="fetchData" :disabled="loading">
        {{ loading ? 'Loading...' : 'Fetch Data' }}
      </button>
      <pre v-if="data">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      title: 'Vue.js Docker App',
      message: 'Welcome to Vue.js with Docker!',
      data: null,
      loading: false
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const response = await fetch('/api/info');
        this.data = await response.json();
      } catch (error) {
        console.error('Error:', error);
      }
      this.loading = false;
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
  text-align: center;
}
button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>
