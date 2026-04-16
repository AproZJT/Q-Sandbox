<template>
  <section class="panel card">
    <h3 class="title">执行状态</h3>
    <p class="meta">{{ statusText }}</p>

    <div class="block">
      <h4>标准输出</h4>
      <pre>{{ stdout || '（暂无输出）' }}</pre>
    </div>

    <div class="block">
      <h4>错误输出</h4>
      <pre>{{ stderr || '（暂无错误）' }}</pre>
    </div>

    <div v-if="result" class="block">
      <h4>结果摘要</h4>
      <p>exit_code: {{ result.exit_code }}</p>
      <p>time_ms: {{ result.time_ms }}</p>
      <p>stage: {{ result.stage }}</p>
      <p>{{ result.summary }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { SandboxResultPayload } from '../types/events'

defineProps<{
  statusText: string
  stdout: string
  stderr: string
  result: SandboxResultPayload | null
}>()
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

.block h4 {
  margin: 0 0 6px;
  font-size: 0.88rem;
  color: var(--stone-gray);
}

.block pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  background: #fff;
  border: 1px solid var(--border-cream);
  border-radius: 8px;
  padding: 10px;
  font-family: var(--font-mono);
  font-size: 0.86rem;
  line-height: 1.55;
}

.block p {
  margin: 2px 0;
  color: var(--charcoal-warm);
}
</style>
