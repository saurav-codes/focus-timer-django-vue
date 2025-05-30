<script setup>
import { useAuthStore } from '../stores/authStore';
import { onMounted } from 'vue';
import { Brain, BarChart2, Clock, Repeat, LogIn, UserPlus, ArrowRight, ChevronDown, Twitter } from 'lucide-vue-next';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// Check if user is already authenticated, redirect to app if they are
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/kanban-planner');
  } else if (localStorage.getItem('accessToken')) {
    // We have a token but store is not initialized
    authStore.initAuth();
    if (authStore.isAuthenticated) {
      router.push('/kanban-planner');
    }
  }
});

// Navigation handlers
const goToLogin = () => {
  router.push('/login');
};

const goToRegister = () => {
  router.push('/register');
};
</script>

<template>
  <div class="homepage">
    <div class="notification-banner">
      Collaborative timer has been temporarily disabled. It will be added back soon.
    </div>
    <header class="header">
      <div class="container">
        <div class="logo-container">
          <h1 class="logo">
            Focus<span>Timer</span>
          </h1>
        </div>
        <nav class="navigation">
          <div class="nav-links">
            <a href="#features" class="nav-link">
              <ChevronDown size="16" class="link-icon" />
              Features
            </a>
          </div>
          <div class="auth-links">
            <button class="login-btn" @click="goToLogin">
              <LogIn size="16" class="button-icon" />
              Log In
            </button>
            <button class="signup-btn" @click="goToRegister">
              <UserPlus size="16" class="button-icon" />
              Get Started
            </button>
          </div>
        </nav>
      </div>
    </header>

    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">
            Plan and Focus Your Day
          </h1>
          <p class="hero-subtitle">
            Create, organize, and track your tasks effortlessly.
          </p>
          <div class="hero-cta">
            <button class="cta-button" @click="goToRegister">
              <ArrowRight size="16" class="button-icon" />
              Improve your Productivity
            </button>
          </div>
        </div>
        <div class="hero-image">
          <div class="video-wrapper">
            <video
              src="@/assets/demo.mp4"
              autoplay
              loop
              muted
              playsinline
              class="hero-img placeholder" />
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="features">
      <div class="container">
        <h2 class="section-title">
          Why choose FocusTimer?
        </h2>
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <Brain size="32" />
            </div>
            <h3 class="feature-title">
              Brain Dump
            </h3>
            <p class="feature-description">
              Quickly capture thoughts and tasks without disrupting your flow. Move seamlessly from ideas to organized plans.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <BarChart2 size="32" />
            </div>
            <h3 class="feature-title">
              Visual Workflow
            </h3>
            <p class="feature-description">
              Intuitive kanban boards help you visualize your work across days, making prioritization effortless.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <Clock size="32" />
            </div>
            <h3 class="feature-title">
              Time Tracking
            </h3>
            <p class="feature-description">
              Built-in time tracking helps you understand where your hours go and improve your time estimates.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <Repeat size="32" />
            </div>
            <h3 class="feature-title">
              Seamless Integrations
            </h3>
            <p class="feature-description">
              Connect with your favorite tools and bring all your tasks into one unified workspace.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="how-it-works">
      <div class="container">
        <h2 class="section-title">
          Your perfect day, every day
        </h2>
        <div class="steps">
          <div class="step">
            <div class="step-number">
              1
            </div>
            <h3 class="step-title">
              Capture
            </h3>
            <p class="step-description">
              Use the Brain Dump to quickly capture all your tasks and ideas without interrupting your flow.
            </p>
          </div>
          <div class="step">
            <div class="step-number">
              2
            </div>
            <h3 class="step-title">
              Organize
            </h3>
            <p class="step-description">
              Drag and drop tasks into your daily planner to create a realistic, achievable schedule.
            </p>
          </div>
          <div class="step">
            <div class="step-number">
              3
            </div>
            <h3 class="step-title">
              Focus
            </h3>
            <p class="step-description">
              Work through your tasks with complete concentration, tracking time and progress as you go.
            </p>
          </div>
          <div class="step">
            <div class="step-number">
              4
            </div>
            <h3 class="step-title">
              Reflect
            </h3>
            <p class="step-description">
              Review your productivity patterns and continuously improve your focus and efficiency.
            </p>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer">
      <div class="footer-bottom">
        <a href="https://x.com/saurav__codes" class="social-link">
          <Twitter size="16" class="link-icon" />
          Contact on Twitter
        </a>
        <p class="copyright">
          © 2025 FocusTimer. All rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.notification-banner {
  background-color: var(--color-warning);
  color: white;
  text-align: center;
  padding: 0.75rem 1rem;
  font-weight: 500;
}
/* Base styles */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Header styles */
.header {
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--color-border);
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.logo span {
  color: var(--color-primary);
}

.navigation {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--color-primary);
}

.auth-links {
  display: flex;
  gap: 1rem;
}

.login-btn,
.signup-btn,
.cta-button,
.pricing-cta {
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
  border: none;
}

/* Hero section */
.hero {
  padding: 5rem 0;
  background-color: var(--color-background);
}

.hero .container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.hero-title {
  font-size: 3.5rem;
  line-height: 1.1;
  font-weight: 800;
  margin-bottom: 1.5rem;
  color: var(--color-text-primary);
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  margin-bottom: 2rem;
  max-width: 500px;
}

.hero-cta {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.cta-button {
  background-color: var(--color-primary);
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.cta-button:hover {
  background-color: var(--color-primary-dark, #4338ca);
}

.secondary-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.2s;
}

.secondary-link:hover {
  color: var(--color-primary);
}

.arrow {
  transition: transform 0.2s;
}

.secondary-link:hover .arrow {
  transform: translateX(5px);
}

.hero-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-img {
  max-width: 100%;
  border-radius: 0.5rem;
  box-shadow: var(--shadow-lg);
}

.placeholder {
  background-color: var(--color-background-secondary);
  min-height: 300px;
  width: 100%;
}

/* Features section */
.features {
  padding: 5rem 0;
  background-color: var(--color-background-secondary);
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 3rem;
  color: var(--color-text-primary);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background-color: var(--color-background);
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.feature-title {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  color: var(--color-text-primary);
}

.feature-description {
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* How it works */
.how-it-works {
  padding: 5rem 0;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.step {
  text-align: center;
  padding: 1.5rem;
}

.step-number {
  background-color: var(--color-primary);
  color: white;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin: 0 auto 1rem;
}

.step-title {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  color: var(--color-text-primary);
}

.step-description {
  color: var(--color-text-secondary);
  line-height: 1.6;
}


/* Pricing section */
.pricing {
  padding: 5rem 0;
}

.pricing-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
}

.pricing-card {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  position: relative;
  transition: transform 0.3s, box-shadow 0.3s;
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.pricing-card.featured {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.popular-badge {
  position: absolute;
  top: -0.75rem;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--color-primary);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.pricing-tier {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary);
}

.pricing-price {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 1.5rem;
}

.pricing-price span {
  font-size: 1rem;
  font-weight: 400;
  color: var(--color-text-tertiary);
}

.pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem;
  text-align: left;
}

.pricing-features li {
  padding: 0.5rem 0;
  color: var(--color-text-secondary);
  position: relative;
  padding-left: 1.5rem;
}

.pricing-features li::before {
  content: "✓";
  color: var(--color-primary);
  position: absolute;
  left: 0;
}

.pricing-cta {
  display: inline-block;
  background-color: var(--color-primary);
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  width: 80%;
  transition: background-color 0.2s;
}

.pricing-cta:hover {
  background-color: var(--color-primary-dark, #4338ca);
}

/* CTA section */
.cta-section {
  padding: 5rem 0;
  background-color: var(--color-primary);
  color: white;
  text-align: center;
}

.cta-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.cta-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-button.large {
  background-color: white;
  color: var(--color-primary);
  font-size: 1.125rem;
  padding: 1rem 2rem;
}

.cta-button.large:hover {
  background-color: rgba(255, 255, 255, 0.9);
}

.footer-tagline {
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  color: var(--color-text-tertiary);
  text-decoration: none;
  transition: color 0.2s;
}

.social-link:hover {
  color: var(--color-primary);
}

.footer-heading {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1.25rem;
}

.footer-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.75rem;
}

.footer-links a {
  color: var(--color-text-tertiary);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--color-primary);
}

.footer-bottom {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.copyright {
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}

/* Media Queries */
@media (max-width: 768px) {
  .hero .container {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-subtitle {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-cta {
    justify-content: center;
  }

  .footer-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }

  .social-links {
    justify-content: center;
  }
}
</style>
