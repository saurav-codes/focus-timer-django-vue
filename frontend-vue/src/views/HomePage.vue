<script setup>
// Import Vue core
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// --- State for sticky nav ---
const isSticky = ref(false)

// --- Demo video state ---
const demoVideoSrc = '/src/assets/demo.mp4'
const fallbackImage = '/src/assets/og-image.png'
const videoLoaded = ref(false)
const videoLoaded2 = ref(false)

// --- Features data ---
const features = [
  {
    id: 1,
    icon: 'Brain',
    title: 'Brain Dump',
    description: 'Quickly jot down thoughts and tasks as they come to you.',
  },
  {
    id: 2,
    icon: 'Clock',
    title: 'Time Blocking',
    description: 'Drag tasks onto your calendar to plan your day visually.',
  },
  {
    id: 3,
    icon: 'BarChart2',
    title: 'Visual Planning',
    description: 'See your day at a glance with a simple, kanban-inspired board.',
  },
  {
    id: 4,
    icon: 'Zap',
    title: 'Simplicity First',
    description: 'No clutter, no distractions—just what you need to get things done.',
  },
]

// --- Roadmap data ---
const roadmapPhases = [
  {
    id: 1,
    title: 'Recurring Tasks & Reminders',
    description: 'Set tasks to repeat and get gentle reminders for what matters.',
    status: 'current',
  },
  {
    id: 2,
    title: 'More Calendar Views',
    description: 'Week and month views for better planning flexibility.',
    status: 'upcoming',
  },
  {
    id: 3,
    title: 'Advanced Keyboard Shortcuts',
    description: 'Work even faster with more keyboard-driven actions.',
    status: 'planned',
  },
  {
    id: 4,
    title: 'Performance & Offline Improvements',
    description: 'Faster load times and basic offline support for peace of mind.',
    status: 'planned',
  },
  {
    id: 5,
    title: 'Integrations',
    description: 'Connect with Google Calendar, Notion, and more (if enough users request).',
    status: 'planned',
  },
]

// --- Router for navigation ---
const router = useRouter()
const signupSection = ref(null)

// --- CTA Handlers ---
function scrollToSignup() {
  // Smooth scroll to the final CTA section
  if (signupSection.value) {
    signupSection.value.scrollIntoView({ behavior: 'smooth' })
  }
}
function goToRegister() {
  // Route to the registration page
  router.push('/register')
}

// --- Video loading handlers ---
function handleVideoLoad() {
  videoLoaded.value = true
}
function handleVideoError() {
  videoLoaded.value = false
}
function handleVideoLoad2() {
  videoLoaded2.value = true
}
function handleVideoError2() {
  videoLoaded2.value = false
}

// --- Sticky nav on scroll ---
onMounted(() => {
  window.addEventListener('scroll', () => {
    isSticky.value = window.scrollY > 32
  })
})
</script>

<template>
  <!-- Main landing page container -->
  <main class="landing-main">
    <!-- Navigation Header -->
    <header class="navigation-header" :class="{ 'sticky': isSticky }">
      <div class="nav-container">
        <div class="logo">
          <h1>Tymr <span class="logo-accent">Online</span></h1>
        </div>
        <button class="nav-cta-button" @click="scrollToSignup">
          Get Free Access
        </button>
      </div>
    </header>

    <!-- Hero Section with gradient background -->
    <section class="hero-section" aria-labelledby="hero-heading">
      <div class="hero-gradient-bg">
        <div class="hero-container">
          <div class="hero-content">
            <h1 id="hero-heading" class="hero-headline">
              Simple, calm productivity for solo creators
            </h1>
            <p class="hero-subtitle">
              Plan your day, block your time, and focus—without the clutter or overwhelm. Tymr Online is a forever-free web app for thoughtful solo work.
            </p>
            <div class="hero-cta">
              <button class="primary-cta-button" @click="scrollToSignup">
                <span class="icon play-icon" aria-hidden="true">
                  <svg width="20" height="20" fill="none" viewBox="0 0 24 24"><circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="2" /><polygon points="10,8 16,12 10,16" fill="currentColor" /></svg>
                </span>
                Try Free Beta
              </button>
              <p class="cta-subtext">
                No credit card. No spam. Just productivity.
              </p>
            </div>
          </div>
          <div class="hero-demo">
            <div class="product-demo-card">
              <video
                ref="demoVideo"
                :src="demoVideoSrc"
                autoplay
                loop
                muted
                playsinline
                class="demo-video"
                tabindex="0"
                aria-label="Product demo video"
                @canplay="handleVideoLoad"
                @error="handleVideoError" />
              <div v-if="!videoLoaded" class="demo-placeholder">
                <img :src="fallbackImage" alt="Tymr Online Interface Preview">
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Beta Status Banner -->
    <section class="beta-banner" aria-label="Beta status">
      <div class="banner-container">
        <div class="banner-icon">
          <svg width="24" height="24" fill="none" viewBox="0 0 24 24"><path
            d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round" /></svg>
        </div>
        <div class="banner-content">
          <h3>Beta: Honest, simple, and evolving</h3>
          <p>
            Tymr Online is in open beta. You might find a bug or two, but your feedback helps shape a tool built for real solo work. Free during beta—always focused on simplicity.
          </p>
        </div>
      </div>
    </section>

    <!-- Feature Showcase -->
    <section class="features-section" aria-labelledby="features-title">
      <div class="features-container">
        <h2 id="features-title" class="section-title">
          Why you'll love Tymr Online
        </h2>
        <div class="features-grid">
          <div v-for="feature in features" :key="feature.id" class="feature-card">
            <div class="feature-icon">
              <span v-if="feature.icon === 'Brain'">
                <svg width="32" height="32" fill="none" viewBox="0 0 24 24"><path
                  d="M15 4a3 3 0 0 1 3 3v1a3 3 0 0 1 3 3v1a3 3 0 0 1-3 3v1a3 3 0 0 1-3 3M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-3 3v1a3 3 0 0 0 3 3v1a3 3 0 0 0 3 3"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round" /></svg>
              </span>
              <span v-else-if="feature.icon === 'Clock'">
                <svg width="32" height="32" fill="none" viewBox="0 0 24 24"><circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="2" /><path
                    d="M12 6v6l4 2"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" /></svg>
              </span>
              <span v-else-if="feature.icon === 'Zap'">
                <svg width="32" height="32" fill="none" viewBox="0 0 24 24"><path
                  d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round" /></svg>
              </span>
              <span v-else-if="feature.icon === 'BarChart2'">
                <svg width="32" height="32" fill="none" viewBox="0 0 24 24"><path
                  d="M3 3v18h18"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round" /><rect
                    x="7"
                    y="13"
                    width="3"
                    height="5"
                    rx="1"
                    fill="currentColor" /><rect
                      x="12"
                      y="9"
                      width="3"
                      height="9"
                      rx="1"
                      fill="currentColor" /><rect
                        x="17"
                        y="5"
                        width="3"
                        height="13"
                        rx="1"
                        fill="currentColor" /></svg>
              </span>
            </div>
            <h3 class="feature-title">
              {{ feature.title }}
            </h3>
            <p class="feature-description">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Honest Roadmap -->
    <section class="roadmap-section" aria-labelledby="roadmap-title">
      <div class="roadmap-container">
        <h2 id="roadmap-title" class="section-title">
          What's next for Tymr Online?
        </h2>
        <div class="roadmap-timeline">
          <div v-for="phase in roadmapPhases" :key="phase.id" class="timeline-item">
            <div class="timeline-marker" :class="phase.status" />
            <div class="timeline-content">
              <h3>{{ phase.title }}</h3>
              <p>{{ phase.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final Call To Action Section -->
    <section ref="signupSection" class="final-cta-section" aria-labelledby="final-cta-headline">
      <div class="cta-container">
        <h2 id="final-cta-headline" class="cta-headline">
          Ready to plan your day with less stress?
        </h2>
        <p class="cta-subtitle">
          Join the beta and help shape a tool built for solo focus.
        </p>
        <button class="large-cta-button" @click="goToRegister">
          <span class="icon arrow-icon" aria-hidden="true">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24"><path
              d="M5 12h14M13 6l6 6-6 6"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round" /></svg>
          </span>
          Get Free Beta Access
        </button>
        <p class="cta-disclaimer">
          Free during beta • No credit card required • No mobile app, just a fast web experience
        </p>
      </div>
    </section>

    <!-- Simple Footer -->
    <footer class="simple-footer" aria-label="Footer">
      <div class="footer-container">
        <span>&copy; {{ new Date().getFullYear() }} Tymr Online. All rights reserved.</span>
        <nav class="footer-links">
          <a href="/privacy-policy" class="footer-link">Privacy Policy</a>
          <a href="/terms-and-conditions" class="footer-link">Terms</a>
        </nav>
      </div>
    </footer>
  </main>
</template>

<style scoped>
.landing-main {
  background: #f8fafc; /* Soft off-white for main background */
  color: #1e293b; /* Very dark gray for text */
  font-family: var(--font-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navigation-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  box-shadow: var(--shadow-sm);
  transition: background var(--transition-base);
}
.navigation-header.sticky {
  background: #fff;
  box-shadow: var(--shadow-md);
}
.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo h1 {
  font-family: var(--font-heading);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: #4338ca; /* Deep indigo */
  margin: 0;
}
.logo-accent {
  color: #0d9488; /* Teal accent */
}
.nav-cta-button {
  background: #4338ca;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: background var(--transition-base), transform var(--transition-base);
}
.nav-cta-button:hover {
  background: #3730a3;
  transform: translateY(-2px);
}

/* Hero Section with light background */
.hero-section {
  padding: 0;
  margin: 0;
}
.hero-gradient-bg {
  background: #f8fafc;
  padding: 4rem 0 2rem 0;
  width: 100%;
}
.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2rem;
  padding: 0 1.5rem;
}
.hero-content {
  flex: 1 1 350px;
  min-width: 300px;
  color: #1e293b;
}
.hero-headline {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: 1rem;
  color: #1e293b;
  text-shadow: none;
}
.hero-subtitle {
  font-size: var(--font-size-xl);
  color: #334155;
  margin-bottom: 2rem;
}
.hero-cta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.primary-cta-button {
  background: #4338ca;
  color: #fff;
  border: none;
  border-radius: 0.75rem;
  padding: 1rem 2.5rem;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: background var(--transition-base), color var(--transition-base), transform var(--transition-base);
}
.primary-cta-button:hover {
  background: #3730a3;
  color: #fff;
  transform: translateY(-2px) scale(1.03);
}
.cta-subtext {
  color: #64748b;
  font-size: var(--font-size-sm);
}
.hero-demo {
  flex: 1 1 350px;
  min-width: 300px;
  display: flex;
  justify-content: center;
}
.product-demo-card {
  width: 100%;
  max-width: 420px;
  border-radius: 1.25rem;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  background: #fff;
  position: relative;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.demo-video {
  width: 100%;
  height: 260px;
  object-fit: cover;
  display: block;
  background: #e2e8f0;
  border-radius: 1rem;
}
.demo-placeholder {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  border-radius: 1rem;
}
.demo-placeholder img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* Beta Status Banner - soft blue, dark text */
.beta-banner {
  background: #e0f2fe;
  color: #1e293b;
  padding: 1.25rem 0;
  display: flex;
  justify-content: center;
  border-radius: 0 0 1.5rem 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
}
.banner-container {
  max-width: 900px;
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
}
.banner-icon {
  flex-shrink: 0;
  margin-top: 0.25rem;
  color: #0d9488;
}
.banner-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: #1e293b;
}
.banner-content p {
  margin: 0;
  font-size: var(--font-size-base);
  color: #334155;
}

/* Feature Showcase - white cards, light gray bg, strong icons */
.features-section {
  background: #f1f5f9;
  padding: 4rem 1rem 2rem 1rem;
  display: flex;
  justify-content: center;
}
.features-container {
  max-width: 1200px;
  width: 100%;
}
.section-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: 2rem;
  color: #4338ca;
  text-align: center;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 2.5rem;
}
.feature-card {
  background: #fff;
  border-radius: 1.25rem;
  box-shadow: var(--shadow-md);
  padding: 2.5rem 1.5rem 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: box-shadow var(--transition-base), transform var(--transition-base);
  cursor: pointer;
  border: 1px solid #e2e8f0;
}
.feature-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-6px) scale(1.04);
}
.feature-icon {
  margin-bottom: 1.25rem;
  color: #4338ca;
  font-size: 2rem;
}
.feature-card svg {
  stroke: #4338ca;
  fill: none;
  width: 2.5rem;
  height: 2.5rem;
  stroke-width: 2.5;
}
.feature-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: 0.5rem;
  text-align: center;
  color: #1e293b;
}
.feature-description {
  color: #334155;
  text-align: center;
  font-size: var(--font-size-base);
}

/* Roadmap Section - subtle bg, clear timeline */
.roadmap-section {
  background: #f8fafc;
  padding: 4rem 1rem 2rem 1rem;
  display: flex;
  justify-content: center;
}
.roadmap-container {
  max-width: 900px;
  width: 100%;
}
.roadmap-timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-top: 2rem;
}
.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}
.timeline-marker {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: #4338ca;
  margin-top: 0.5rem;
  flex-shrink: 0;
  border: 3px solid #fff;
  transition: background var(--transition-base);
}
.timeline-marker.current {
  background: #4338ca;
}
.timeline-marker.upcoming {
  background: #0d9488;
}
.timeline-marker.planned {
  background: #64748b;
}
.timeline-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: #1e293b;
}
.timeline-content p {
  margin: 0 0 0.25rem 0;
  color: #334155;
}

/* Final CTA Section - white bg, strong CTA */
.final-cta-section {
  background: #fff;
  color: #1e293b;
  padding: 4rem 1rem 2rem 1rem;
  display: flex;
  justify-content: center;
}
.cta-container {
  max-width: 600px;
  width: 100%;
  text-align: center;
}
.cta-headline {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: 1rem;
  color: #1e293b;
}
.cta-subtitle {
  font-size: var(--font-size-lg);
  margin-bottom: 2rem;
  color: #334155;
}
.large-cta-button {
  background: #4338ca;
  color: #fff;
  border: none;
  border-radius: 0.75rem;
  padding: 1rem 2.5rem;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: background var(--transition-base), color var(--transition-base), transform var(--transition-base);
  margin: 0 auto 1rem auto;
}
.large-cta-button:hover {
  background: #3730a3;
  color: #fff;
  transform: translateY(-2px) scale(1.03);
}
.cta-disclaimer {
  color: #64748b;
  font-size: var(--font-size-sm);
  margin-top: 0.5rem;
}

/* Footer */
.simple-footer {
  background: #f1f5f9;
  color: #64748b;
  padding: 2rem 1rem 1rem 1rem;
  display: flex;
  justify-content: center;
}
.footer-container {
  max-width: 900px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.footer-links {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
}
.footer-link {
  color: #4338ca;
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
  transition: color var(--transition-base);
}
.footer-link:hover {
  color: #0d9488;
}

/* Responsive Design */
@media (max-width: 900px) {
  .hero-container, .features-container, .roadmap-container {
    max-width: 98vw;
    padding: 0 0.5rem;
  }
}
@media (max-width: 700px) {
  .hero-container {
    flex-direction: column;
    gap: 2rem;
    align-items: stretch;
  }
  .hero-content, .hero-demo {
    min-width: 0;
  }
  .features-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 500px) {
  .hero-gradient-bg, .features-section, .roadmap-section, .final-cta-section {
    padding: 2rem 0.25rem 1rem 0.25rem;
  }
  .product-demo-card, .demo-video {
    height: 180px;
  }
}
</style>
