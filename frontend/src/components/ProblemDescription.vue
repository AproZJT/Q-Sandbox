<template>
  <section class="card problem">
    <p class="badge">题目描述</p>
    <h2>{{ title }}</h2>
    <p class="desc">{{ description }}</p>

    <div class="meta-grid">
      <div>
        <span class="label">输入</span>
        <p>{{ inputSpec }}</p>
      </div>
      <div>
        <span class="label">输出</span>
        <p>{{ outputSpec }}</p>
      </div>
      <div>
        <span class="label">示例</span>
        <pre>{{ sample }}</pre>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
  inputSpec: string
  outputSpec: string
  sample: string
}>()
</script>

<style scoped>
.problem {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.badge {
  margin: 0;
  display: inline-flex;
  width: fit-content;
  font-size: 0.72rem;
  letter-spacing: 0.3px;
  color: var(--stone-gray);
  text-transform: uppercase;
}

h2 {
  margin: 0;
  font-family: var(--font-serif);
  font-weight: 500;
  font-size: 1.58rem;
  line-height: 1.2;
}

.desc {
  margin: 0;
  color: var(--olive-gray);
}

.meta-grid {
  margin-top: 4px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.label {
  font-size: 0.75rem;
  color: var(--stone-gray);
}

.meta-grid p,
.meta-grid pre {
  margin: 4px 0 0;
  font-size: 0.9rem;
  color: var(--charcoal-warm);
  white-space: pre-wrap;
  line-height: 1.55;
}

.meta-grid pre {
  font-family: var(--font-mono);
  background: #fff;
  border: 1px solid var(--border-cream);
  border-radius: 8px;
  padding: 8px;
}

@media (max-width: 900px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
