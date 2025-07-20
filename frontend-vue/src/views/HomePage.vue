<script setup>
// Import Vue core
import { LucideArrowDownRight, LucideGift } from 'lucide-vue-next'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// Import images
import screenshotLight from '@/assets/screenshot-light.png'
import screenshotDark from '@/assets/screenshot-dark.png'

// --- State for sticky nav ---
const isSticky = ref(false)

// --- Ultra-smooth demo animation state ---
const demoImages = [
  screenshotLight,
  screenshotDark
]
const isLoaded = ref(false)
const animationPhase = ref(0) // 0-7 for 8 different movement patterns
const animationFrame = ref()

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
  {
    id: 5,
    icon: 'AppWindow',
    title: '3rd Party Integrations',
    description: 'Connect with Google Calendar, Gmail, GitHub, and more (if enough users request).',
  },
  {
    id: 6,
    icon: 'Repeat',
    title: 'Recurring Tasks & Reminders',
    description: 'Set tasks to repeat and get gentle reminders for what matters.',
  },
  {
    id: 7,
    icon: 'Carry',
    title: 'Auto-Carry Over Tasks',
    description: 'Tasks that were not completed from the previous day are carried over to the next day.',
  },
  {
    id: 8,
    icon: 'Archive',
    title: 'Auto Archive Tasks after 30 days',
    description: 'Tasks with 30 days of inactivity are automatically archived.',
  },
]

// --- Roadmap data ---
const roadmapPhases = [
  {
    id: 1,
    title: 'Themes',
    description: 'Dark, light, and other themes for your preference.',
    status: 'current',
  },
  {
    id: 2,
    title: 'AI assisted labels & project assignment',
    description: 'AI will help you label and assign projects to tasks.',
    status: 'upcoming',
  },
  {
    id: 3,
    title: 'More Calendar Views',
    description: 'Week and month views for better planning flexibility.',
    status: 'upcoming',
  },
  {
    id: 4,
    title: 'Advanced Keyboard Shortcuts',
    description: 'Work even faster with more keyboard-driven actions.',
    status: 'planned',
  },
  {
    id: 5,
    title: 'Performance & Offline Support',
    description: 'Faster load times and basic offline support for peace of mind.',
    status: 'planned',
  },
  {
    id: 6,
    title: '3rd Party Integrations',
    description: 'Connect with Outlook, Notion, Todoist, and more (if enough users request).',
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





// --- Ultra-smooth 120fps-like animation logic ---
function startUltraSmoothAnimation() {
  let startTime = Date.now()

  function animate() {
    const elapsed = Date.now() - startTime
    const cycle = elapsed / 12000 // 12 second full cycle for smoother mirror effect

    // Ultra-smooth continuous phase calculation (0 to 2π for smooth sine waves)
    animationPhase.value = (cycle % 1) * Math.PI * 2

    // Continue animation at maximum smoothness
    animationFrame.value = requestAnimationFrame(animate)
  }

  animate()
}



// --- Sticky nav on scroll ---
onMounted(() => {
  window.addEventListener('scroll', () => {
    isSticky.value = window.scrollY > 32
  })

  // Initial load animation
  setTimeout(() => {
    isLoaded.value = true
  }, 100)

  // Start the ultra-smooth demo animation after initial load
  setTimeout(() => {
    startUltraSmoothAnimation()
  }, 1000)
})
</script>

<template>
  <!-- Skip links for keyboard navigation -->
  <div class="skip-links">
    <a href="#hero-heading" class="skip-link">Skip to main content</a>
    <a href="#features-title" class="skip-link">Skip to features</a>
    <a href="#roadmap-title" class="skip-link">Skip to roadmap</a>
    <a href="#final-cta-headline" class="skip-link">Skip to signup</a>
  </div>

  <!-- Main landing page container -->
  <main class="landing-main" role="main">
    <!-- Navigation Header -->
    <header class="navigation-header" :class="{ 'sticky': isSticky }" role="banner">
      <div class="nav-container">
        <div class="logo">
          <h1
            tabindex="0"
            role="button"
            aria-label="LazyPlanner.com - Go to homepage"
            @click="$router.push('/')"
            @keydown.enter="$router.push('/')"
            @keydown.space.prevent="$router.push('/')">
            Lazy<span class="logo-accent">Planner</span>
          </h1>
        </div>
        <button class="nav-cta-button" aria-label="Get free access - scroll to signup section" @click="scrollToSignup">
          Get Free Access
          <LucideGift :size="16" />
        </button>
      </div>
    </header>

    <!-- Hero Section with gradient background -->
    <section class="hero-section" aria-labelledby="hero-heading">
      <div class="hero-gradient-bg">
        <div class="hero-container">
          <div class="hero-content">
            <h1 id="hero-heading" class="hero-headline">
              <span class="accent-text" tabindex="0" role="text" aria-label="Simple - emphasized word">Simple</span>,
              <span class="accent-text" tabindex="0" role="text" aria-label="calm - emphasized word">calm</span>
              productivity for <span
                class="accent-text"
                tabindex="0"
                role="text"
                aria-label="solo creators - emphasized phrase">solo creators</span>
            </h1>
            <p class="hero-subtitle">
              Plan your day/week, block your time, and focus without the clutter or overwhelm.
            </p>
            <p>
              A Daily Planner web app for thoughtful solo work.
            </p>
            <div class="hero-cta">
              <button
                class="primary-cta-button"
                aria-label="Try free beta - scroll to signup section"
                @click="scrollToSignup">
                <span class="icon play-icon" aria-hidden="true">
                  <svg
                    width="20"
                    height="20"
                    fill="none"
                    viewBox="0 0 24 24"
                    role="img"
                    aria-hidden="true">
                    <circle
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="2" />
                    <polygon points="10,8 16,12 10,16" fill="currentColor" />
                  </svg>
                </span>
                Plan My Day
                <LucideArrowDownRight :size="16" />
              </button>
              <p class="cta-subtext">
                No credit card. No spam. Just productivity.
              </p>
            </div>
          </div>
          <div class="hero-demo">
            <div class="ultra-smooth-demo-container" :class="{ 'loaded': isLoaded }">
              <!-- Ultra-smooth infinite animation canvas -->
              <div class="infinite-animation-canvas">
                <!-- Continuous flowing background effects -->
                <div class="flowing-gradient-bg" />

                <!-- Mirror Effect Image System -->
                <div class="mirror-effect-container" :style="{ '--phase': animationPhase }">
                  <!-- Primary Image (Dark Theme - Front Layer) -->
                  <div class="primary-image-layer">
                    <img :src="demoImages[1]" alt="LazyPlanner.com Dark Theme Interface" class="primary-screenshot">
                  </div>

                  <!-- Mirror Image (Light Theme - Back Layer) -->
                  <div class="mirror-image-layer">
                    <img :src="demoImages[0]" alt="LazyPlanner.com Light Theme Interface" class="mirror-screenshot">
                  </div>

                  <!-- Reflection Overlay -->
                  <div class="reflection-overlay" />
                </div>

                <!-- Ultra-smooth particle system -->
                <div class="ultra-particles">
                  <div
                    v-for="n in 20"
                    :key="n"
                    class="ultra-particle"
                    :style="{
                      '--index': n,
                      '--phase': animationPhase
                    }" />
                </div>

                <!-- Flowing light rays -->
                <div class="light-rays">
                  <div v-for="n in 8" :key="n" class="light-ray" :style="{ '--ray-index': n }" />
                </div>

                <!-- Dynamic theme indicator -->
                <div class="dynamic-theme-indicator">
                  <div
                    class="theme-pulse"
                    :class="{
                      'dark-active': Math.sin(animationPhase) > 0,
                      'light-active': Math.sin(animationPhase) <= 0
                    }" />
                </div>
              </div>

              <div id="demo-description" class="sr-only">
                Ultra-smooth animated demonstration of LazyPlanner.com's interface continuously flowing between light
                and dark themes with dynamic particle effects
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Beta Status Banner -->
    <section class="beta-banner" aria-label="Beta status">
      <div class="banner-container">
        <div class="banner-icon" tabindex="0" role="img" aria-label="Lightning bolt icon indicating beta status">
          <svg
            width="24"
            height="24"
            fill="none"
            viewBox="0 0 24 24"
            role="img"
            aria-hidden="true">
            <path
              d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round" />
          </svg>
        </div>
        <div class="banner-content">
          <h3>Beta: Honest, simple, and evolving</h3>
          <p>
            LazyPlanner is in beta. You might find a bug or two, but your feedback helps shape a tool built for
            real solo work. Free during beta & always focused on simplicity.
          </p>
        </div>
      </div>
    </section>
    <!-- Feature Showcase -->
    <section class="features-section" aria-labelledby="features-title">
      <div class="features-container">
        <h2 id="features-title" class="section-title" tabindex="0">
          Why you'll love LazyPlanner
        </h2>
        <div class="features-grid">
          <div
            v-for="feature in features"
            :key="feature.id"
            class="feature-card"
            tabindex="0"
            role="article"
            :aria-labelledby="`feature-title-${feature.id}`"
            :aria-describedby="`feature-desc-${feature.id}`">
            <div class="feature-icon">
              <span v-if="feature.icon === 'Brain'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <path
                    d="M15 4a3 3 0 0 1 3 3v1a3 3 0 0 1 3 3v1a3 3 0 0 1-3 3v1a3 3 0 0 1-3 3M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-3 3v1a3 3 0 0 0 3 3v1a3 3 0 0 0 3 3"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
              <span v-else-if="feature.icon === 'Clock'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="2" />
                  <path
                    d="M12 6v6l4 2"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
              <span v-else-if="feature.icon === 'Zap'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <path
                    d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
              <span v-else-if="feature.icon === 'BarChart2'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <path
                    d="M3 3v18h18"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                  <rect
                    x="7"
                    y="13"
                    width="3"
                    height="5"
                    rx="1"
                    fill="currentColor" />
                  <rect
                    x="12"
                    y="9"
                    width="3"
                    height="9"
                    rx="1"
                    fill="currentColor" />
                  <rect
                    x="17"
                    y="5"
                    width="3"
                    height="13"
                    rx="1"
                    fill="currentColor" />
                </svg>
              </span>
              <span v-else-if="feature.icon === 'AppWindow'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <path
                    d="M3 12h18M3 6h18M3 18h18"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
              <span v-else-if="feature.icon === 'Archive'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <path
                    d="M5 12h14M13 6l6 6-6 6"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
              <span v-else-if="feature.icon === 'Repeat'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <path
                    d="M12 6v6l4 2"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
              <span v-else-if="feature.icon === 'Carry'" role="img" :aria-label="`${feature.title} icon`">
                <svg
                  width="32"
                  height="32"
                  fill="none"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-hidden="true">
                  <path
                    d="M5 12h14M13 6l6 6-6 6"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
            </div>
            <h3 :id="`feature-title-${feature.id}`" class="feature-title">
              {{ feature.title }}
            </h3>
            <p :id="`feature-desc-${feature.id}`" class="feature-description">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Honest Roadmap -->
    <section class="roadmap-section" aria-labelledby="roadmap-title">
      <div class="roadmap-container">
        <h2 id="roadmap-title" class="section-title" tabindex="0">
          What's next for LazyPlanner.?
        </h2>
        <div class="roadmap-timeline">
          <div
            v-for="phase in roadmapPhases"
            :key="phase.id"
            class="timeline-item"
            tabindex="0"
            role="article"
            :aria-labelledby="`roadmap-title-${phase.id}`"
            :aria-describedby="`roadmap-desc-${phase.id} roadmap-status-${phase.id}`">
            <div class="timeline-marker" :class="phase.status" role="img" :aria-label="`Status: ${phase.status}`">
              <!-- Visual indicators for status beyond just color -->
              <span v-if="phase.status === 'current'" class="status-indicator" aria-hidden="true">●</span>
              <span v-else-if="phase.status === 'upcoming'" class="status-indicator" aria-hidden="true">◐</span>
              <span v-else class="status-indicator" aria-hidden="true">○</span>
            </div>
            <div class="timeline-content">
              <h3 :id="`roadmap-title-${phase.id}`">
                {{ phase.title }}
              </h3>
              <p :id="`roadmap-desc-${phase.id}`">
                {{ phase.description }}
              </p>
              <span :id="`roadmap-status-${phase.id}`" class="sr-only">Status: {{ phase.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final Call To Action Section -->
    <section ref="signupSection" class="final-cta-section" aria-labelledby="final-cta-headline">
      <div class="cta-container">
        <h2 id="final-cta-headline" class="cta-headline" tabindex="0">
          Ready to plan your day with less stress?
        </h2>
        <p class="cta-subtitle">
          Join the beta and help shape a tool built for solo focus.
        </p>
        <button
          class="large-cta-button"
          aria-label="Get free beta access - go to registration page"
          @click="goToRegister">
          <span class="icon arrow-icon" aria-hidden="true">
            <svg
              width="20"
              height="20"
              fill="none"
              viewBox="0 0 24 24"
              role="img"
              aria-hidden="true">
              <path
                d="M5 12h14M13 6l6 6-6 6"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round" />
            </svg>
          </span>
          Plan today ( Fully free during Beta )
        </button>
        <p class="cta-disclaimer">
          Free during beta • No credit card required • No mobile app, just a fast web experience
        </p>
      </div>
    </section>

    <!-- Simple Footer -->
    <footer class="simple-footer" aria-label="Footer">
      <div class="footer-container">
        <span>&copy; {{ new Date().getFullYear() }} LazyPlanner.com. All rights reserved.</span>
        <nav class="footer-links" role="navigation" aria-label="Footer navigation">
          <a href="/privacy-policy" target="_blank" class="footer-link">Privacy Policy</a>
          <a href="/terms-and-conditions" target="_blank" class="footer-link">Terms</a>
          <a href="https://x.com/saurav__codes" target="_blank" class="footer-link">Contact</a>
          <!-- made by saurav__codes -->
          <a href="https://sorv.dev" target="_blank" class="footer-link">Made by @SauravSharma</a>
        </nav>
      </div>
    </footer>
  </main>
</template>

<style scoped>
/* Dark theme custom properties - WCAG AA compliant */
:root {
  /* Core dark theme color palette */
  --dark-bg-primary: #000000;
  --dark-bg-secondary: #111111;
  --dark-bg-tertiary: #1A1A1A;
  --dark-bg-footer: #0A0A0A;

  /* Text color hierarchy - WCAG AA compliant contrast ratios */
  --dark-text-primary: #FFFFFF;
  /* 21:1 contrast ratio on black */
  --dark-text-secondary: #B3B3B3;
  /* 7.5:1 contrast ratio on black - improved from #A0A0A0 */
  --dark-text-tertiary: #808080;
  /* 4.6:1 contrast ratio on black - improved from #666666 */
  --dark-text-muted: #999999;
  /* 5.7:1 contrast ratio on black */

  /* Accent colors - Enhanced for better contrast */
  --dark-accent-primary: #4AEAE0;
  /* Brighter teal for better contrast - 12.8:1 on black */
  --dark-accent-hover: #3DD4C7;
  /* Hover state with good contrast */
  --dark-accent-variant: #2DD4BF;
  /* Variant color */
  --dark-accent-focus: #5BFFF5;
  /* High contrast focus color */

  /* Border colors */
  --dark-border-subtle: #333333;
  --dark-border-muted: #222222;
  --dark-border-focus: #4AEAE0;
  /* Focus border color */

  /* Status colors for roadmap - accessible variants */
  --dark-status-current: #4AEAE0;
  /* Current items - high contrast */
  --dark-status-upcoming: #2DD4BF;
  /* Upcoming items */
  --dark-status-planned: #999999;
  /* Planned items - muted but readable */

  /* Animation and transition properties */
  --transition-duration: 0.2s;
  --transition-easing: cubic-bezier(0.4, 0, 0.2, 1);
  --lift-transform: translateY(-4px);
  --lift-transform-small: translateY(-2px);
  --lift-transform-large: translateY(-6px);

  /* Focus indicator properties */
  --focus-ring-width: 2px;
  --focus-ring-offset: 2px;
  --focus-ring-color: var(--dark-accent-focus);
  --focus-ring-style: solid;
}

.landing-main {
  background: var(--dark-bg-primary);
  color: var(--dark-text-primary);
  font-family: var(--font-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navigation-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--dark-bg-primary);
  box-shadow: var(--shadow-sm);
  transition: background var(--transition-base);
}

.navigation-header.sticky {
  background: var(--dark-bg-primary);
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
  color: var(--dark-text-primary);
  margin: 0;
  cursor: pointer;
  transition: all var(--transition-duration) var(--transition-easing);
}

.logo h1:hover {
  transform: var(--lift-transform-small);
}

.logo-accent {
  color: var(--dark-accent-primary);
  transition: all var(--transition-duration) var(--transition-easing);
}

.logo h1:hover .logo-accent {
  color: var(--dark-accent-hover);
  text-shadow: 0 0 8px rgba(64, 224, 208, 0.4);
}

.logo h1:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: 0.25rem;
}

.nav-cta-button {
  background: var(--dark-accent-primary);
  color: var(--dark-bg-primary);
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-duration) var(--transition-easing);
}

.nav-cta-button:hover {
  background: var(--dark-accent-hover);
  transform: var(--lift-transform-small);
  box-shadow: var(--shadow-md);
}

.nav-cta-button:active {
  transform: translateY(0);
  transition-duration: 0.1s;
}

.nav-cta-button:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

/* Hero Section with dark background */
.hero-section {
  padding: 0;
  margin: 0;
}

.hero-gradient-bg {
  background: var(--dark-bg-primary);
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
  color: var(--dark-text-primary);
}

.hero-headline {
  font-size: 4.5rem;
  /* 72px */
  font-weight: 300;
  margin-bottom: 1rem;
  color: var(--dark-text-primary);
  text-shadow: none;
  line-height: 1.1;
}

.hero-headline .accent-text {
  color: var(--dark-accent-primary);
  transition: all var(--transition-duration) var(--transition-easing);
  cursor: pointer;
}

.hero-headline .accent-text:hover {
  color: var(--dark-accent-hover);
  text-shadow: 0 0 12px rgba(64, 224, 208, 0.5);
  transform: scale(1.05);
}

.hero-headline .accent-text:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: 0.25rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  /* 20px */
  color: var(--dark-text-secondary);
  margin-bottom: 2rem;
}

.hero-cta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.primary-cta-button {
  background: var(--dark-accent-primary);
  color: var(--dark-bg-primary);
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
  transition: all var(--transition-duration) var(--transition-easing);
}

.primary-cta-button:hover {
  background: var(--dark-accent-hover);
  color: var(--dark-bg-primary);
  transform: var(--lift-transform-small) scale(1.02);
  box-shadow: var(--shadow-lg);
}

.primary-cta-button:active {
  transform: translateY(0) scale(1);
  transition-duration: 0.1s;
}

.primary-cta-button .icon {
  transition: transform var(--transition-duration) var(--transition-easing);
}

.primary-cta-button:hover .icon {
  transform: scale(1.1);
}

.primary-cta-button:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

.cta-subtext {
  color: var(--dark-text-muted);
  font-size: var(--font-size-sm);
}

.hero-demo {
  flex: 1 1 350px;
  min-width: 300px;
  display: flex;
  justify-content: center;
}



/* Ultra-Smooth Demo Animation System */
.ultra-smooth-demo-container {
  width: 100%;
  max-width: 480px;
  height: 320px;
  position: relative;
  background: var(--dark-bg-secondary);
  opacity: 0;
  transform: translateY(30px) scale(0.9);
  transition: all 1s cubic-bezier(0.4, 0, 0.2, 1);

  /* Clean modern shadow without borders */
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
}

.ultra-smooth-demo-container.loaded {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.ultra-smooth-demo-container:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 35px 70px -12px rgba(0, 0, 0, 0.5);
}

/* Infinite Animation Canvas */
.infinite-animation-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* Ultra-soft edge fade overlay - matching hero section colors */
.infinite-animation-canvas::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 10;
  background:
    /* Horizontal fade - using hero section background color */
    linear-gradient(to right,
      var(--dark-bg-primary) 0%,
      rgba(0, 0, 0, 0.5) 8%,
      transparent 20%,
      transparent 80%,
      rgba(0, 0, 0, 0.5) 92%,
      var(--dark-bg-primary) 100%),
    /* Vertical fade - using hero section background color */
    linear-gradient(to bottom,
      var(--dark-bg-primary) 0%,
      rgba(0, 0, 0, 0.5) 8%,
      transparent 20%,
      transparent 80%,
      rgba(0, 0, 0, 0.5) 92%,
      var(--dark-bg-primary) 100%);
}

/* Continuous Flowing Background */
.flowing-gradient-bg {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: conic-gradient(from 0deg,
      rgba(74, 234, 224, 0.1) 0deg,
      rgba(45, 212, 191, 0.15) 90deg,
      rgba(74, 234, 224, 0.1) 180deg,
      rgba(45, 212, 191, 0.05) 270deg,
      rgba(74, 234, 224, 0.1) 360deg);
  animation: rotateGradient 20s linear infinite;
  z-index: 1;
}

@keyframes rotateGradient {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* Ultra-Smooth Mirror Effect System */
.mirror-effect-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  perspective: 1000px;
}

/* Primary Image Layer (Dark Theme - Front) */
.primary-image-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 3;
  will-change: transform, opacity;

  /* Much further distance for proper interchanging */
  transform:
    translateZ(calc(sin(var(--phase)) * 120px)) rotateY(calc(sin(var(--phase)) * 8deg)) scale(calc(1 + sin(var(--phase)) * 0.08));

  opacity: calc(0.9 + sin(var(--phase)) * 0.1);

  transition: all 0.016s linear;
}

/* Mirror Image Layer (Light Theme - Back) */
.mirror-image-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  will-change: transform, opacity;

  /* Opposite animation with much further distance */
  transform:
    translateZ(calc(sin(var(--phase) + 3.14159) * 100px)) rotateY(calc(sin(var(--phase) + 3.14159) * 6deg)) scale(calc(1 + sin(var(--phase) + 3.14159) * 0.06));

  opacity: calc(0.8 + sin(var(--phase) + 3.14159) * 0.2);

  transition: all 0.016s linear;
}

/* Screenshot styling */
.primary-screenshot,
.mirror-screenshot {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  will-change: transform;
}

/* Clean mirror screenshot without vintage effects */
.mirror-screenshot {
  filter: brightness(0.95) saturate(1.05);
}

/* Clean reflection overlay - modern accent colors */
.reflection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 4;
  pointer-events: none;
  background:
    linear-gradient(135deg,
      rgba(74, 234, 224, 0.08) 0%,
      transparent 25%,
      transparent 75%,
      rgba(74, 234, 224, 0.04) 100%);

  /* Subtle animation that follows the primary layer */
  opacity: calc(0.4 + sin(var(--phase)) * 0.3);
  transform: translateZ(calc(sin(var(--phase)) * 60px));

  transition: all 0.016s linear;
}

/* Ultra-Smooth Particle System */
.ultra-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 3;
}

.ultra-particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: var(--dark-accent-primary);
  border-radius: 50%;
  box-shadow: 0 0 6px var(--dark-accent-primary);

  /* Dynamic positioning based on index and phase */
  left: calc(5% + (var(--index) * 4.5%));
  top: calc(10% + (var(--index) * 4%));

  /* Ultra-smooth continuous movement */
  transform:
    translateX(calc(sin(var(--phase) + var(--index)) * 30px)) translateY(calc(cos(var(--phase) + var(--index)) * 20px)) scale(calc(0.5 + sin(var(--phase) * 2 + var(--index)) * 0.5));

  opacity: calc(0.3 + sin(var(--phase) + var(--index)) * 0.4);

  transition: all 0.1s linear;
  will-change: transform, opacity;
}

/* Flowing Light Rays */
.light-rays {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 4;
}

.light-ray {
  position: absolute;
  width: 2px;
  height: 100%;
  background: linear-gradient(to bottom,
      transparent 0%,
      rgba(74, 234, 224, 0.3) 50%,
      transparent 100%);

  left: calc(10% + (var(--ray-index) * 10%));

  transform:
    translateX(calc(sin(var(--ray-index) * 0.5) * 20px)) scaleY(calc(0.5 + sin(var(--ray-index)) * 0.5));

  animation: flowRay calc(3s + var(--ray-index) * 0.5s) ease-in-out infinite;
  will-change: transform;
}

@keyframes flowRay {

  0%,
  100% {
    opacity: 0.2;
    transform: translateX(0) scaleY(0.5);
  }

  50% {
    opacity: 0.6;
    transform: translateX(10px) scaleY(1);
  }
}

/* Dynamic Theme Indicator */
.dynamic-theme-indicator {
  position: absolute;
  bottom: 15px;
  right: 15px;
  z-index: 5;
}

.theme-pulse {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--dark-accent-primary);
  box-shadow: 0 0 20px var(--dark-accent-primary);
  transition: all 0.3s ease;
}

.theme-pulse.light-active {
  background: #fbbf24;
  box-shadow: 0 0 20px #fbbf24;
  animation: pulseBright 2s ease-in-out infinite;
}

.theme-pulse.dark-active {
  background: #8b5cf6;
  box-shadow: 0 0 20px #8b5cf6;
  animation: pulseDark 2s ease-in-out infinite;
}

@keyframes pulseBright {

  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}

@keyframes pulseDark {

  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

/* Beta Status Banner - dark theme */
.beta-banner {
  background: var(--dark-bg-secondary);
  color: var(--dark-text-primary);
  padding: 1.25rem 0;
  display: flex;
  justify-content: center;
  border-radius: 0 0 1.5rem 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--dark-border-subtle);
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
  color: var(--dark-accent-primary);
  transition: all var(--transition-duration) var(--transition-easing);
  cursor: pointer;
}

.banner-icon:hover {
  color: var(--dark-accent-hover);
  transform: scale(1.1) rotate(10deg);
}

.banner-icon:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: 0.25rem;
}

.banner-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--dark-text-primary);
}

.banner-content p {
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--dark-text-secondary);
}

/* Feature Showcase - dark theme cards */
.features-section {
  background: var(--dark-bg-primary);
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
  color: var(--dark-text-primary);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-duration) var(--transition-easing);
}

.section-title:hover {
  color: var(--dark-accent-primary);
  transform: var(--lift-transform-small);
}

.section-title:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: 0.25rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 2.5rem;
}

.feature-card {
  background: var(--dark-bg-secondary);
  border-radius: 1.25rem;
  box-shadow: var(--shadow-md);
  padding: 2.5rem 1.5rem 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all var(--transition-duration) var(--transition-easing);
  cursor: pointer;
  border: 1px solid var(--dark-border-subtle);
}

.feature-card:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
  transform: var(--lift-transform);
  border-color: var(--dark-accent-primary);
}

.feature-card:active {
  transform: var(--lift-transform-small);
  transition-duration: 0.1s;
}

.feature-card:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

.feature-icon {
  margin-bottom: 1.25rem;
  color: var(--dark-accent-primary);
  font-size: 2rem;
  transition: all var(--transition-duration) var(--transition-easing);
}

.feature-card:hover .feature-icon {
  color: var(--dark-accent-hover);
  transform: scale(1.1) rotate(5deg);
}

.feature-card svg {
  stroke: var(--dark-accent-primary);
  fill: none;
  width: 2.5rem;
  height: 2.5rem;
  stroke-width: 2.5;
  transition: all var(--transition-duration) var(--transition-easing);
}

.feature-card:hover svg {
  stroke: var(--dark-accent-hover);
  stroke-width: 3;
}

.feature-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: 0.5rem;
  text-align: center;
  color: var(--dark-text-primary);
}

.feature-description {
  color: var(--dark-text-secondary);
  text-align: center;
  font-size: var(--font-size-base);
}

/* Roadmap Section - enhanced dark theme timeline */
.roadmap-section {
  background: var(--dark-bg-primary);
  padding: 4rem 1rem 2rem 1rem;
  display: flex;
  justify-content: center;
  position: relative;
}

.roadmap-container {
  max-width: 900px;
  width: 100%;
}

.roadmap-timeline {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  margin-top: 2rem;
  position: relative;
}

/* Add connecting line for better visual flow */
.roadmap-timeline::before {
  content: '';
  position: absolute;
  left: 0.75rem;
  top: 1.5rem;
  bottom: 1.5rem;
  width: 2px;
  background: linear-gradient(to bottom,
      var(--dark-accent-primary) 0%,
      var(--dark-accent-variant) 40%,
      var(--dark-text-tertiary) 100%);
  z-index: 1;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  position: relative;
  z-index: 2;
  cursor: pointer;
  transition: all var(--transition-duration) var(--transition-easing);
  padding: 0.5rem;
  border-radius: 0.5rem;
}

.timeline-item:hover {
  background: rgba(74, 234, 224, 0.05);
  transform: var(--lift-transform-small);
}

.timeline-item:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: 0.5rem;
  background: rgba(74, 234, 224, 0.05);
}

.timeline-marker {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  margin-top: 0.5rem;
  flex-shrink: 0;
  border: 3px solid var(--dark-bg-primary);
  transition: all var(--transition-duration) var(--transition-easing);
  box-shadow: 0 0 0 2px var(--dark-bg-primary);
  position: relative;
  z-index: 3;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.timeline-marker.current {
  background: var(--dark-status-current);
  box-shadow: 0 0 0 2px var(--dark-bg-primary), 0 0 12px rgba(74, 234, 224, 0.4);
}

.timeline-marker.current:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 2px var(--dark-bg-primary), 0 0 20px rgba(74, 234, 224, 0.6);
}

.timeline-marker.upcoming {
  background: var(--dark-status-upcoming);
  box-shadow: 0 0 0 2px var(--dark-bg-primary), 0 0 8px rgba(45, 212, 191, 0.3);
}

.timeline-marker.upcoming:hover {
  transform: scale(1.15);
  box-shadow: 0 0 0 2px var(--dark-bg-primary), 0 0 16px rgba(45, 212, 191, 0.5);
}

.timeline-marker.planned {
  background: var(--dark-status-planned);
  opacity: 0.8;
  /* Improved from 0.6 for better visibility */
  box-shadow: 0 0 0 2px var(--dark-bg-primary);
}

.timeline-marker.planned:hover {
  transform: scale(1.1);
  opacity: 1;
  /* Full opacity on hover for better accessibility */
}

/* Status indicators for accessibility - not relying on color alone */
.status-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  line-height: 1;
  color: var(--dark-bg-primary);
  font-weight: bold;
}

.timeline-content {
  flex: 1;
  padding: 0.25rem 0;
}

.timeline-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--dark-text-primary);
  line-height: 1.4;
}

.timeline-content p {
  margin: 0;
  color: var(--dark-text-secondary);
  line-height: 1.6;
  font-size: var(--font-size-base);
}

/* Enhanced visual contrast for current items */
.timeline-item:has(.timeline-marker.current) .timeline-content h3 {
  color: var(--dark-text-primary);
  font-weight: var(--font-weight-bold);
}

.timeline-item:has(.timeline-marker.current) .timeline-content p {
  color: var(--dark-text-secondary);
}

/* Subtle styling for planned items - improved contrast */
.timeline-item:has(.timeline-marker.planned) .timeline-content h3 {
  color: var(--dark-text-secondary);
}

.timeline-item:has(.timeline-marker.planned) .timeline-content p {
  color: var(--dark-text-muted);
  /* Better contrast than tertiary */
}

/* Final CTA Section - dark secondary bg */
.final-cta-section {
  background: var(--dark-bg-secondary);
  color: var(--dark-text-primary);
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
  color: var(--dark-text-primary);
  cursor: pointer;
  transition: all var(--transition-duration) var(--transition-easing);
}

.cta-headline:hover {
  color: var(--dark-accent-primary);
  transform: var(--lift-transform-small);
}

.cta-headline:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: 0.25rem;
}

.cta-subtitle {
  font-size: var(--font-size-lg);
  margin-bottom: 2rem;
  color: var(--dark-text-secondary);
}

.large-cta-button {
  background: var(--dark-accent-primary);
  color: var(--dark-bg-primary);
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
  transition: all var(--transition-duration) var(--transition-easing);
  margin: 0 auto 1rem auto;
}

.large-cta-button:hover {
  background: var(--dark-accent-hover);
  color: var(--dark-bg-primary);
  transform: var(--lift-transform-large) scale(1.05);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
}

.large-cta-button:active {
  transform: var(--lift-transform-small) scale(1.02);
  transition-duration: 0.1s;
}

.large-cta-button .icon {
  transition: transform var(--transition-duration) var(--transition-easing);
}

.large-cta-button:hover .icon {
  transform: translateX(4px) scale(1.1);
}

.large-cta-button:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

.cta-disclaimer {
  color: var(--dark-text-muted);
  font-size: var(--font-size-sm);
  margin-top: 0.5rem;
}

/* Footer - Dark theme with clear page termination */
.simple-footer {
  background: var(--dark-bg-footer);
  /* #0A0A0A - darkest secondary background */
  color: var(--dark-text-tertiary);
  padding: 2rem 1rem 1rem 1rem;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--dark-border-muted);
  margin-top: auto;
  /* Push footer to bottom */
}

.footer-container {
  max-width: 900px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.footer-container span {
  color: var(--dark-text-muted);
  /* Better contrast than tertiary */
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
}

.footer-links {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.footer-link {
  color: var(--dark-accent-primary);
  /* Teal color for links */
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
  transition: all var(--transition-duration) var(--transition-easing);
  position: relative;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.footer-link:hover {
  color: var(--dark-accent-hover);
  /* Teal hover state */
  transform: var(--lift-transform-small);
  background: rgba(64, 224, 208, 0.1);
}

.footer-link:focus {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: 0.25rem;
}

.footer-link:active {
  transform: translateY(0);
  transition-duration: 0.1s;
}

/* Skip links for keyboard navigation */
.skip-links {
  position: absolute;
  top: -100px;
  left: 0;
  z-index: 1000;
}

.skip-link {
  position: absolute;
  top: -100px;
  left: 0;
  background: var(--dark-accent-primary);
  color: var(--dark-bg-primary);
  padding: 0.5rem 1rem;
  text-decoration: none;
  font-weight: var(--font-weight-semibold);
  border-radius: 0 0 0.25rem 0;
  transition: top var(--transition-duration) var(--transition-easing);
}

.skip-link:focus {
  top: 0;
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Enhanced focus indicators for better accessibility */
*:focus-visible {
  outline: var(--focus-ring-width) var(--focus-ring-style) var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

/* Ensure interactive elements have minimum touch target size */
button,
[role="button"],
a {
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  :root {
    --dark-text-secondary: #FFFFFF;
    --dark-text-tertiary: #FFFFFF;
    --dark-text-muted: #FFFFFF;
    --dark-accent-primary: #FFFFFF;
    --dark-accent-hover: #FFFFFF;
    --focus-ring-color: #FFFFFF;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {

  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  .timeline-marker:hover,
  .feature-card:hover,
  .timeline-item:hover,
  .primary-cta-button:hover,
  .large-cta-button:hover,
  .nav-cta-button:hover {
    transform: none !important;
  }

  /* Disable ultra-smooth animations for reduced motion */
  .ultra-particle,
  .light-ray,
  .flowing-gradient-bg {
    display: none;
  }

  .image-slide {
    transition: opacity 0.5s ease !important;
    transform: none !important;
  }

  .theme-pulse {
    animation: none !important;
  }
}

/* Responsive Design */
@media (max-width: 900px) {

  .hero-container,
  .features-container,
  .roadmap-container {
    max-width: 98vw;
    padding: 0 0.5rem;
  }

  .hero-headline {
    font-size: 3.5rem;
    /* Medium size for tablets */
  }
}

@media (max-width: 700px) {
  .hero-container {
    flex-direction: column;
    gap: 2rem;
    align-items: stretch;
  }

  .hero-content,
  .hero-demo {
    min-width: 0;
  }

  .hero-headline {
    font-size: 2.5rem;
    /* Smaller on mobile */
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 500px) {

  .hero-gradient-bg,
  .features-section,
  .roadmap-section,
  .final-cta-section {
    padding: 2rem 0.25rem 1rem 0.25rem;
  }

  .ultra-smooth-demo-container {
    height: 240px;
    max-width: 100%;
  }

  /* Responsive roadmap timeline adjustments */
  .roadmap-timeline {
    gap: 2rem;
  }

  .timeline-item {
    gap: 1rem;
  }

  .timeline-marker {
    width: 1.25rem;
    height: 1.25rem;
    margin-top: 0.375rem;
  }

  .roadmap-timeline::before {
    left: 0.625rem;
  }

  .timeline-content h3 {
    font-size: var(--font-size-base);
  }

  .timeline-content p {
    font-size: var(--font-size-sm);
  }
}
</style>
