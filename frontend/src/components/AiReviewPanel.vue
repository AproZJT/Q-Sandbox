<template>
  <section class="panel card">
    <h3 class="title">AI 点评</h3>
    <p class="meta">{{ statusText }}</p>
    <article class="content" v-html="renderedHtml"></article>
  </section>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { computed } from 'vue'

const props = defineProps<{
  statusText: string
  reviewText: string
}>()

const md = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: true,
})

const renderedHtml = computed(() => md.render(props.reviewText || '（等待 AI 输出）'))
</script>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.title {
  margin: 0;
  font-family: var(--font-serif);
  font-weight: 500;
  font-size: 1.3rem;
  color: var(--near-black);
}

.meta {
  margin: 0;
  color: var(--olive-gray);
  font-size: 0.95rem;
}

.content {
  min-height: 200px;
  background: #fffdf8;
  border: 1px dashed var(--border-warm);
  border-radius: 12px;
  padding: 14px;
  line-height: 1.6;
  color: var(--charcoal-warm);
}

.content :deep(pre) {
  background: #fff;
  border: 1px solid var(--border-cream);
  border-radius: 8px;
  padding: 10px;
  overflow-x: auto;
}

.content :deep(code) {
  font-family: var(--font-mono);
}
</style>
