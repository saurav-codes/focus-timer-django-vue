<script setup>
  import { ref } from 'vue'
  import { GitPullRequest, GitMerge, GitBranch, AlertCircle } from 'lucide-vue-next'

  // Mock GitHub data
  const repositories = ref([
    {
      id: 1,
      name: 'focus-timer-vue',
      pullRequests: 3,
      issues: 5,
      lastCommit: '2 hours ago',
      branch: 'main',
    },
    {
      id: 2,
      name: 'productivity-dashboard',
      pullRequests: 1,
      issues: 2,
      lastCommit: 'yesterday',
      branch: 'develop',
    },
    {
      id: 3,
      name: 'task-management-api',
      pullRequests: 0,
      issues: 8,
      lastCommit: '3 days ago',
      branch: 'feature/auth',
    },
  ])

  // Get status icon based on PR and issue count
  const getStatusIcon = (repo) => {
    if (repo.pullRequests > 0) {
      return GitPullRequest
    } else if (repo.issues > 0) {
      return AlertCircle
    } else {
      return GitMerge
    }
  }

  // Get status color based on PR and issue count
  const getStatusColor = (repo) => {
    if (repo.pullRequests > 0) {
      return 'var(--color-primary, #89b4fa)'
    } else if (repo.issues > 0) {
      return 'var(--color-warning, #f9e2af)'
    } else {
      return 'var(--color-success, #a6e3a1)'
    }
  }
</script>

<template>
  <div class="github-integration">
    <div class="integration-header">
      <h3>GitHub</h3>
      <div class="repo-count">{{ repositories.length }} repositories</div>
    </div>

    <div class="repositories-list">
      <div v-for="repo in repositories" :key="repo.id" class="repo-card">
        <div class="repo-header">
          <div class="repo-name">{{ repo.name }}</div>
          <div class="repo-branch">
            <GitBranch size="14" />
            <span>{{ repo.branch }}</span>
          </div>
        </div>

        <div class="repo-stats">
          <div class="repo-stat">
            <GitPullRequest size="14" />
            <span>{{ repo.pullRequests }} PRs</span>
          </div>
          <div class="repo-stat">
            <AlertCircle size="14" />
            <span>{{ repo.issues }} issues</span>
          </div>
          <div class="repo-last-commit">Last commit: {{ repo.lastCommit }}</div>
        </div>

        <div class="repo-status" :style="{ backgroundColor: getStatusColor(repo) }">
          <component :is="getStatusIcon(repo)" size="14" />
        </div>
      </div>

      <div v-if="repositories.length === 0" class="no-repos">No repositories found</div>
    </div>
  </div>
</template>

<style scoped>
  .github-integration {
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

  .repo-count {
    font-size: 14px;
    color: var(--color-text-secondary, #a6adc8);
  }

  .repositories-list {
    flex: 1;
  }

  .repo-card {
    position: relative;
    padding: 12px;
    margin-bottom: 8px;
    background-color: var(--color-background, #1e1e2e);
    border-radius: 8px;
    border: 1px solid var(--color-border, #313244);
  }

  .repo-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .repo-name {
    font-size: 14px;
    font-weight: 500;
  }

  .repo-branch {
    display: flex;
    align-items: center;
    font-size: 12px;
    color: var(--color-text-secondary, #a6adc8);
  }

  .repo-branch svg {
    margin-right: 4px;
  }

  .repo-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .repo-stat {
    display: flex;
    align-items: center;
    font-size: 12px;
    color: var(--color-text-tertiary, #7f849c);
  }

  .repo-stat svg {
    margin-right: 4px;
  }

  .repo-last-commit {
    font-size: 12px;
    color: var(--color-text-tertiary, #7f849c);
    margin-top: 4px;
  }

  .repo-status {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-background, #1e1e2e);
  }

  .no-repos {
    text-align: center;
    padding: 24px;
    color: var(--color-text-tertiary, #7f849c);
    font-style: italic;
  }
</style>
