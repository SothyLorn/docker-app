// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Disable server-side rendering for static export
  ssr: false,
  
  // Static site generation
  nitro: {
    preset: 'static'
  },
  
  // App configuration
  app: {
    head: {
      title: 'Nuxt.js Docker App',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Nuxt.js application with Docker' }
      ]
    }
  },

  // Development server configuration
  devServer: {
    port: 3000
  }
})
