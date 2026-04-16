<template>
  <section class="card history">
    <div class="head">
      <h3>最近提交</h3>
      <span class="tip">最多保留 {{ maxItems }} 条</span>
    </div>

    <ul v-if="items.length" class="list">
      <li v-for="item in items" :key="item.submissionId" class="row">
        <div class="meta">
          <p class="id">{{ shortId(item.submissionId) }}</p>
          <p class="desc">{{ item.mode }} · {{ item.createdAtLabel }}</p>
        </div>
        <button class="replay" @click="$emit('replay', item.streamUrl)">回放</button>
      </li>
    </ul>

    <p v-else class="empty">暂无历史提交。</p>
  </section>
</template>

<script setup lang="ts">
export interface HistoryItem {
  submissionId: string
  streamUrl: string
  mode: 'review' | 'socratic'
  createdAtLabel: string
}

defineProps<{
  items: HistoryItem[]
  maxItems: number
}>()

defineEmits<{
  (event: 'replay', streamUrl: string): void
}>()

function shortId(id: string): string {
  return id.length > 12 ? `${id.slice(0, 8)}...${id.slice(-4)}` : id
}
</script>

<style scoped>
.history { display: flex; flex-direction: column; gap: 10px; }
.head { display: flex; justify-content: space-between; align-items: center; }
.head h3 { margin: 0; font-family: var(--font-serif); font-weight: 500; }
.tip { font-size: 12px; color: var(--stone-gray); }
.list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 8px; border: 1px solid var(--border-cream); border-radius: 10px; background: #fff; }
.id { margin: 0; font-family: var(--font-mono); font-size: 12px; color: var(--charcoal-warm); }
.desc { margin: 2px 0 0; font-size: 12px; color: var(--stone-gray); }
.replay { border: 1px solid var(--border-warm); background: var(--warm-sand); color: var(--charcoal-warm); border-radius: 8px; padding: 6px 10px; cursor: pointer; }
.empty { margin: 0; color: var(--stone-gray); }
</style>
