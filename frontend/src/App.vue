<template>
  <div class="page">
    <header class="topbar card">
      <div>
        <h1>Q-Sandbox</h1>
        <p>一个尽量轻量的本地编程练习小项目</p>
      </div>
      <button :disabled="running" @click="run">
        {{ running ? '运行中...' : '运行并查看结果' }}
      </button>
    </header>

    <ProblemDescription
      title="A + B 问题"
      description="读取两个整数 a 与 b，输出它们的和。"
      input-spec="一行两个整数 a b。"
      output-spec="输出一个整数，表示 a+b。"
      sample="输入: 1 2\n输出: 3"
    />

    <main class="layout">
      <section class="left card">
        <h2>代码编辑区（C++）</h2>
        <CodeEditor v-model="sourceCode" />
      </section>

      <section class="right">
        <SandboxPanel
          :status-text="sandboxStatus"
          :stdout="sandboxStdout"
          :stderr="sandboxStderr"
          :result="sandboxResult"
        />
        <AiReviewPanel :status-text="llmStatus" :review-text="llmText" />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AiReviewPanel from './components/AiReviewPanel.vue'
import CodeEditor from './components/CodeEditor.vue'
import ProblemDescription from './components/ProblemDescription.vue'
import SandboxPanel from './components/SandboxPanel.vue'
import { createSubmission, toStreamUrl } from './api/submission'
import type { SandboxResultPayload } from './types/events'

const running = ref(false)
const sourceCode = ref(`#include <iostream>
int main() {
  int a, b;
  std::cin >> a >> b;
  std::cout << a + b;
  return 0;
}`)

const sandboxStatus = ref('等待运行')
const sandboxStdout = ref('')
const sandboxStderr = ref('')
const sandboxResult = ref<SandboxResultPayload | null>(null)

const llmStatus = ref('等待点评')
const llmText = ref('')

let es: EventSource | null = null

function resetPanels() {
  sandboxStatus.value = '任务已提交，等待沙箱执行'
  sandboxStdout.value = ''
  sandboxStderr.value = ''
  sandboxResult.value = null
  llmStatus.value = '等待模型开始输出'
  llmText.value = ''
}

function closeStream() {
  if (es) {
    es.close()
    es = null
  }
}

function bindSSE(streamUrl: string) {
  closeStream()
  es = new EventSource(streamUrl)

  const eventTypes = [
    'submission.accepted',
    'sandbox.queued',
    'sandbox.running',
    'sandbox.stdout',
    'sandbox.stderr',
    'sandbox.result',
    'llm.start',
    'llm.delta',
    'llm.end',
    'done',
    'error',
  ]

  eventTypes.forEach((type) => {
    es?.addEventListener(type, (event) => {
      const data = JSON.parse(event.data) as { payload: Record<string, unknown> }

      if (type === 'sandbox.queued' || type === 'sandbox.running') {
        sandboxStatus.value = String(data.payload.message ?? type)
      }

      if (type === 'sandbox.stdout') sandboxStdout.value += String(data.payload.chunk ?? '')
      if (type === 'sandbox.stderr') sandboxStderr.value += String(data.payload.chunk ?? '')

      if (type === 'sandbox.result') {
        sandboxResult.value = data.payload as unknown as SandboxResultPayload
        sandboxStatus.value = String(data.payload.summary ?? '沙箱执行结束')
      }

      if (type === 'llm.start') llmStatus.value = '模型正在生成点评...'
      if (type === 'llm.delta') llmText.value += String(data.payload.delta ?? '')
      if (type === 'llm.end') llmStatus.value = '点评生成完成'

      if (type === 'error') {
        llmStatus.value = `流程异常：${String(data.payload.message ?? 'unknown')}`
        running.value = false
        closeStream()
      }

      if (type === 'done') {
        running.value = false
        closeStream()
      }
    })
  })

  es.onerror = () => {
    if (running.value) {
      llmStatus.value = '连接异常或服务提前结束'
      running.value = false
    }
    closeStream()
  }
}

async function run() {
  running.value = true
  resetPanels()

  try {
    const created = await createSubmission({
      problem_id: 'demo-001',
      language: 'cpp',
      mode: 'review',
      source_code: sourceCode.value,
    })

    bindSSE(toStreamUrl(created.stream_url))
  } catch (error) {
    running.value = false
    llmStatus.value = `提交失败：${error instanceof Error ? error.message : String(error)}`
  }
}
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}

.topbar h1 {
  margin: 0;
  font-family: var(--font-serif);
  font-weight: 600;
  font-size: clamp(1.7rem, 2.6vw, 2.3rem);
}

.topbar p { margin: 6px 0 0; color: var(--olive-gray); }
.layout { display: grid; grid-template-columns: 1.45fr 1fr; gap: 16px; }
.left { display: flex; flex-direction: column; gap: 12px; }
.left h2 { margin: 0; font-family: var(--font-serif); font-weight: 500; }
.right { display: flex; flex-direction: column; gap: 16px; }

button {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  background: var(--terracotta);
  color: var(--ivory);
  font-weight: 600;
  cursor: pointer;
}
button:disabled { opacity: 0.62; cursor: not-allowed; }

@media (max-width: 1140px) { .layout { grid-template-columns: 1fr; } }
@media (max-width: 768px) {
  .page { padding: 12px; }
  .topbar { flex-direction: column; align-items: flex-start; }
  button { width: 100%; }
}
</style>
