<template>
  <div ref="editorRoot" class="editor-root"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
}>()

const editorRoot = ref<HTMLElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null
let syncingFromOutside = false

onMounted(() => {
  if (!editorRoot.value) return

  editor = monaco.editor.create(editorRoot.value, {
    value: props.modelValue,
    language: 'cpp',
    theme: 'vs',
    fontFamily: 'Consolas, "Anthropic Mono", monospace',
    fontSize: 15,
    minimap: { enabled: false },
    automaticLayout: true,
    scrollBeyondLastLine: false,
    roundedSelection: true,
    lineNumbersMinChars: 3,
    padding: { top: 16, bottom: 16 },
  })

  editor.onDidChangeModelContent(() => {
    if (!editor || syncingFromOutside) return
    emit('update:modelValue', editor.getValue())
  })
})

watch(
  () => props.modelValue,
  (value) => {
    if (!editor) return
    const current = editor.getValue()
    if (current === value) return

    syncingFromOutside = true
    editor.setValue(value)
    syncingFromOutside = false
  },
)

onBeforeUnmount(() => {
  editor?.dispose()
})
</script>

<style scoped>
.editor-root {
  height: 420px;
  border: 1px solid var(--border-cream);
  border-radius: 12px;
  overflow: hidden;
  background: var(--ivory);
  box-shadow: var(--ring-shadow);
}
</style>
