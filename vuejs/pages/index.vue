<template>
  <div class="container">
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    <button @click="fetchData" :disabled="loading">
      {{ loading ? 'Loading...' : 'Fetch Data' }}
    </button>
    <pre v-if="data">{{ JSON.stringify(data, null, 2) }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = 'Nuxt.js Docker App'
const message = 'Welcome to Nuxt.js with Docker!'
const data = ref(null)
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/info')
    data.value = await response.json()
  } catch (error) {
    console.error('Error:', error)
  }
  loading.value = false
}
</script>

<style scoped>
.container {
  padding: 20px;
  text-align: center;
}

h1 {
  font-size: 3rem;
  margin-bottom: 20px;
  color: #00dc82;
}

p {
  font-size: 1.5rem;
  margin-bottom: 30px;
}

button {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  margin: 10px;
  background-color: #00dc82;
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: bold;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #00b868;
}

pre {
  background-color: #1e1e1e;
  color: #00dc82;
  padding: 20px;
  border-radius: 5px;
  text-align: left;
  overflow-x: auto;
  max-width: 500px;
  margin: 20px auto;
}
</style>
