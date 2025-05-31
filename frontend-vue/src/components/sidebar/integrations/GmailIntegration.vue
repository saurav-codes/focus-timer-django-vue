<script setup>
  import { ref } from 'vue'
  import { Star, StarOff, Paperclip } from 'lucide-vue-next'

  // Mock email data
  const emails = ref([
    {
      id: 1,
      sender: 'John Smith',
      email: 'john.smith@example.com',
      subject: 'Project Update - Q3 Goals',
      preview: 'Hi team, I wanted to share the latest updates on our Q3 goals...',
      time: '10:23 AM',
      isStarred: true,
      hasAttachment: true,
      isRead: false,
    },
    {
      id: 2,
      sender: 'Product Team',
      email: 'product@company.com',
      subject: 'New Feature Release',
      preview: 'We are excited to announce the launch of our newest feature...',
      time: 'Yesterday',
      isStarred: false,
      hasAttachment: false,
      isRead: true,
    },
    {
      id: 3,
      sender: 'Sarah Johnson',
      email: 'sarah.j@client.org',
      subject: 'Meeting Feedback',
      preview: 'Thank you for the presentation yesterday. I had a few thoughts...',
      time: 'Mar 1',
      isStarred: true,
      hasAttachment: false,
      isRead: true,
    },
  ])

  const toggleStar = (emailId) => {
    const email = emails.value.find((e) => e.id === emailId)
    if (email) {
      email.isStarred = !email.isStarred
    }
  }
</script>

<template>
  <div class="gmail-integration">
    <div class="integration-header">
      <h3>Gmail</h3>
      <div class="email-count">{{ emails.length }} emails</div>
    </div>

    <div class="emails-list">
      <div v-for="email in emails" :key="email.id" class="email-card" :class="{ unread: !email.isRead }">
        <div class="email-actions">
          <button class="star-btn" @click="toggleStar(email.id)">
            <Star v-if="email.isStarred" size="16" class="starred" />
            <StarOff v-else size="16" />
          </button>
        </div>

        <div class="email-content">
          <div class="email-sender">
            {{ email.sender }}
          </div>
          <div class="email-subject">
            {{ email.subject }}
          </div>
          <div class="email-preview">
            {{ email.preview }}
          </div>
        </div>

        <div class="email-meta">
          <div class="email-time">
            {{ email.time }}
          </div>
          <Paperclip v-if="email.hasAttachment" size="14" class="attachment-icon" />
        </div>
      </div>

      <div v-if="emails.length === 0" class="no-emails">Your inbox is empty</div>
    </div>
  </div>
</template>

<style scoped>
  .gmail-integration {
    padding: 16px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .integration-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .integration-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text, #cdd6f4);
  }

  .email-count {
    font-size: 14px;
    color: var(--color-text-secondary, #a6adc8);
  }

  .emails-list {
    flex: 1;
  }

  .email-card {
    display: flex;
    padding: 12px;
    margin-bottom: 8px;
    background-color: var(--color-background, #1e1e2e);
    border-radius: 8px;
    border: 1px solid var(--color-border, #313244);
  }

  .email-card.unread {
    background-color: var(--color-background-light, #313244);
    border-left: 3px solid var(--color-primary, #89b4fa);
  }

  .email-actions {
    display: flex;
    flex-direction: column;
    margin-right: 12px;
  }

  .star-btn {
    background: transparent;
    border: none;
    color: var(--color-text-tertiary, #7f849c);
    cursor: pointer;
    padding: 0;
  }

  .star-btn .starred {
    color: var(--color-warning, #f9e2af);
  }

  .email-content {
    flex: 1;
    min-width: 0; /* Ensures text truncation works */
  }

  .email-sender {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .email-subject {
    font-size: 14px;
    font-weight: 400;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
