//./plugins/posthog.js
import posthog from 'posthog-js'

export default {
  install(app) {
    app.config.globalProperties.$posthog = posthog.init('phc_n2n6vnB0bfJXUbipqTbhIwqhlxy0reVXXkXF0KYgMI0', {
      api_host: 'https://us.i.posthog.com',
    })
    console.log('PostHog initialized in production mode')
  },
}
