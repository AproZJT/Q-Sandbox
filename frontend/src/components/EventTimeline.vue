<template>
  <section class="card timeline">
    <div class="timeline-header">
      <h3>事件时间线</h3>
      <span class="count">{{ filteredEvents.length }} / {{ events.length }} 条</span>
    </div>

    <div class="filters">
      <button
        v-for="item in filterOptions"
        :key="item.id"
        class="chip"
        :class="{ active: item.id === filter }"
        @click="filter = item.id"
      >
        {{ item.label }}
      </button>
    </div>

    <ul v-if="filteredEvents.length" class="timeline-list">
      <li v-for="item in filteredEvents" :key="`${item.event_id}-${item.type}`" class="timeline-item">
        <div class="dot" :class="dotClass(item.type)"></div>
        <div class="content">
          <p class="type">{{ item.type }}</p>
          <p class="time">{{ formatTs(item.ts) }}</p>
          <pre>{{ compactPayload(item.payload) }}</pre>
        </div>
      </li>
    </ul>

    <p v-else class="empty">该分类暂无事件。</p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { SSEEnvelope } from '../types/events'

type FilterId = 'all' | 'sandbox' | 'llm' | 'error' | 'system'

const props = defineProps<{
  events: SSEEnvelope<Record<string, unknown>>[]
}>()

const filter = ref<FilterId>('all')

const filterOptions: { id: FilterId; label: string }[] = [
  { id: 'all', label: '全部' },
  { id: 'sandbox', label: '沙箱' },
  { id: 'llm', label: 'LLM' },
  { id: 'error', label: '异常' },
  { id: 'system', label: '系统' },
]

const filteredEvents = computed(() => {
  if (filter.value === 'all') return props.events
  if (filter.value === 'sandbox') return props.events.filter((e) => e.type.startsWith('sandbox.'))
  if (filter.value === 'llm') return props.events.filter((e) => e.type.startsWith('llm.'))
  if (filter.value === 'error') return props.events.filter((e) => e.type === 'error')
  return props.events.filter((e) => e.type.startsWith('submission.') || e.type === 'done')
})

function formatTs(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleTimeString()
}

function compactPayload(payload: Record<string, unknown>): string {
  return JSON.stringify(payload, null, 2)
}

function dotClass(type: string): string {
  if (type === 'error') return 'error'
  if (type.startsWith('llm.')) return 'llm'
  if (type.startsWith('sandbox.')) return 'sandbox'
  return 'system'
}
</script>

<style scoped>
.timeline {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-header h3 {
  margin: 0;
  font-family: var(--font-serif);
  font-weight: 500;
  color: var(--near-black);
}

.count {
  font-size: 0.82rem;
  color: var(--stone-gray);
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  border: 1px solid var(--border-warm);
  background: #fff;
  color: var(--charcoal-warm);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
}

.chip.active {
  background: var(--warm-sand);
  box-shadow: var(--ring-shadow);
}

.timeline-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  overflow: auto;
}

.timeline-item {
  display: grid;
  grid-template-columns: 12px 1fr;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  margin-top: 5px;
  border-radius: 999px;
  background: var(--terracotta);
  box-shadow: 0 0 0 1px #c9644260;
}
.dot.llm { background: #d97757; }
.dot.sandbox { background: #5e5d59; }
.dot.error { background: #b53333; }
.dot.system { background: #87867f; }

.content {
  border: 1px solid var(--border-cream);
  background: #fff;
  border-radius: 10px;
  padding: 8px 10px;
}

.type { margin: 0; font-size: 0.88rem; color: var(--charcoal-warm); font-weight: 600; }
.time { margin: 2px 0 6px; font-size: 0.75rem; color: var(--stone-gray); }

.content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--olive-gray);
  line-height: 1.4;
}

.empty { margin: 0; color: var(--stone-gray); }
</style>
