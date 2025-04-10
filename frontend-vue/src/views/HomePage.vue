<script setup>
// No complex logic needed for the landing page at this point
</script>

<template>
  <div class="homepage">
    <header class="header">
      <div class="container">
        <div class="logo-container">
          <h1 class="logo">Focus<span>Timer</span></h1>
        </div>
        <nav class="navigation">
          <div class="nav-links">
            <a href="#features" class="nav-link">Features</a>
            <a href="#pricing" class="nav-link">Pricing</a>
            <a href="#testimonials" class="nav-link">Testimonials</a>
          </div>
          <div class="auth-links">
            <!-- These will be actual links later when we implement auth -->
            <router-link to="/kanban-planner" class="login-btn">Log In</router-link>
            <router-link to="/kanban-planner" class="signup-btn">Get Started</router-link>
          </div>
        </nav>
      </div>
    </header>

    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">Master Your Day, <br>One Task at a Time</h1>
          <p class="hero-subtitle">
            The all-in-one productivity platform that combines deep focus with intelligent planning to transform how you work.
          </p>
          <div class="hero-cta">
            <router-link to="/kanban-planner" class="cta-button">Try For Free</router-link>
            <a href="#features" class="secondary-link">See how it works <span class="arrow">→</span></a>
          </div>
        </div>
        <div class="hero-image">
          <img src="@/assets/hero-image.svg" alt="FocusTimer app interface" class="hero-img placeholder" />
        </div>
      </div>
    </section>

    <section id="features" class="features">
      <div class="container">
        <h2 class="section-title">Why choose FocusTimer?</h2>
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3 class="feature-title">Brain Dump</h3>
            <p class="feature-description">
              Quickly capture thoughts and tasks without disrupting your flow. Move seamlessly from ideas to organized plans.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">Visual Workflow</h3>
            <p class="feature-description">
              Intuitive kanban boards help you visualize your work across days, making prioritization effortless.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⏱️</div>
            <h3 class="feature-title">Time Tracking</h3>
            <p class="feature-description">
              Built-in time tracking helps you understand where your hours go and improve your time estimates.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔄</div>
            <h3 class="feature-title">Seamless Integrations</h3>
            <p class="feature-description">
              Connect with your favorite tools and bring all your tasks into one unified workspace.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="how-it-works">
      <div class="container">
        <h2 class="section-title">Your perfect day, every day</h2>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <h3 class="step-title">Capture</h3>
            <p class="step-description">
              Use the Brain Dump to quickly capture all your tasks and ideas without interrupting your flow.
            </p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h3 class="step-title">Organize</h3>
            <p class="step-description">
              Drag and drop tasks into your daily planner to create a realistic, achievable schedule.
            </p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h3 class="step-title">Focus</h3>
            <p class="step-description">
              Work through your tasks with complete concentration, tracking time and progress as you go.
            </p>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <h3 class="step-title">Reflect</h3>
            <p class="step-description">
              Review your productivity patterns and continuously improve your focus and efficiency.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section id="testimonials" class="testimonials">
      <div class="container">
        <h2 class="section-title">What our users say</h2>
        <div class="testimonial-grid">
          <div class="testimonial-card">
            <p class="testimonial-text">
              "FocusTimer has transformed my workday. The Brain Dump feature alone has saved me countless hours of mental overhead."
            </p>
            <div class="testimonial-author">
              <img src="" alt="" class="author-img placeholder" />
              <div class="author-info">
                <p class="author-name">Alex Johnson</p>
                <p class="author-role">Product Manager</p>
              </div>
            </div>
          </div>
          <div class="testimonial-card">
            <p class="testimonial-text">
              "As a freelancer, I juggle multiple projects daily. FocusTimer helps me stay on track and deliver consistently."
            </p>
            <div class="testimonial-author">
              <img src="" alt="" class="author-img placeholder" />
              <div class="author-info">
                <p class="author-name">Sarah Chen</p>
                <p class="author-role">UX Designer</p>
              </div>
            </div>
          </div>
          <div class="testimonial-card">
            <p class="testimonial-text">
              "The time tracking feature has been eye-opening. I now understand where my time goes and have doubled my productivity."
            </p>
            <div class="testimonial-author">
              <img src="" alt="" class="author-img placeholder" />
              <div class="author-info">
                <p class="author-name">Michael Rivera</p>
                <p class="author-role">Software Engineer</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="pricing" class="pricing">
      <div class="container">
        <h2 class="section-title">Simple, transparent pricing</h2>
        <div class="pricing-options">
          <div class="pricing-card">
            <h3 class="pricing-tier">Free</h3>
            <p class="pricing-price">$0<span>/month</span></p>
            <ul class="pricing-features">
              <li>Brain Dump feature</li>
              <li>Basic kanban planning</li>
              <li>3-day planning horizon</li>
              <li>Up to 20 active tasks</li>
            </ul>
            <router-link to="/kanban-planner" class="pricing-cta">Get Started</router-link>
          </div>
          <div class="pricing-card featured">
            <div class="popular-badge">Most Popular</div>
            <h3 class="pricing-tier">Pro</h3>
            <p class="pricing-price">$9<span>/month</span></p>
            <ul class="pricing-features">
              <li>Everything in Free</li>
              <li>Unlimited tasks</li>
              <li>14-day planning horizon</li>
              <li>Time tracking</li>
              <li>Basic integrations</li>
            </ul>
            <router-link to="/kanban-planner" class="pricing-cta">Start Free Trial</router-link>
          </div>
          <div class="pricing-card">
            <h3 class="pricing-tier">Team</h3>
            <p class="pricing-price">$19<span>/user/month</span></p>
            <ul class="pricing-features">
              <li>Everything in Pro</li>
              <li>Team collaboration</li>
              <li>Task delegation</li>
              <li>Advanced integrations</li>
              <li>Priority support</li>
            </ul>
            <router-link to="/kanban-planner" class="pricing-cta">Contact Sales</router-link>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-section">
      <div class="container">
        <h2 class="cta-title">Ready to transform your productivity?</h2>
        <p class="cta-subtitle">Join thousands of professionals who have reclaimed their focus and mastered their time.</p>
        <router-link to="/kanban-planner" class="cta-button large">Get Started For Free</router-link>
      </div>
    </section>

    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <h2 class="footer-logo">Focus<span>Timer</span></h2>
            <p class="footer-tagline">Master your day, one task at a time</p>
            <div class="social-links">
              <a href="#" class="social-link">Twitter</a>
              <a href="#" class="social-link">LinkedIn</a>
              <a href="#" class="social-link">GitHub</a>
            </div>
          </div>
          <div class="footer-links">
            <h3 class="footer-heading">Product</h3>
            <ul>
              <li><a href="#">Features</a></li>
              <li><a href="#">Pricing</a></li>
              <li><a href="#">Integrations</a></li>
              <li><a href="#">Roadmap</a></li>
            </ul>
          </div>
          <div class="footer-links">
            <h3 class="footer-heading">Resources</h3>
            <ul>
              <li><a href="#">Blog</a></li>
              <li><a href="#">Tutorials</a></li>
              <li><a href="#">Support</a></li>
              <li><a href="#">API Docs</a></li>
            </ul>
          </div>
          <div class="footer-links">
            <h3 class="footer-heading">Company</h3>
            <ul>
              <li><a href="#">About Us</a></li>
              <li><a href="#">Careers</a></li>
              <li><a href="#">Privacy</a></li>
              <li><a href="#">Terms</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p class="copyright">© 2023 FocusTimer. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
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

.login-btn {
  color: var(--color-text-primary);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: var(--color-background-secondary);
}

.signup-btn {
  background-color: var(--color-primary);
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.signup-btn:hover {
  background-color: var(--color-primary-dark, #4338ca);
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

/* Testimonials */
.testimonials {
  padding: 5rem 0;
  background-color: var(--color-background-secondary);
}

.testimonial-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.testimonial-card {
  background-color: var(--color-background);
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: var(--shadow-sm);
}

.testimonial-text {
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--color-text-primary);
  margin-bottom: 1.5rem;
  font-style: italic;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-img {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background-color: var(--color-background-tertiary);
}

.author-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.author-role {
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
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

/* Footer */
.footer {
  background-color: var(--color-background-secondary);
  padding: 5rem 0 2rem;
  color: var(--color-text-secondary);
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 3rem;
  margin-bottom: 3rem;
}

.footer-logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.75rem;
}

.footer-logo span {
  color: var(--color-primary);
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
