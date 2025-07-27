<template>
  <main class="container">
    <h1>Design your Schema</h1>
    <br />
    <div class="vue-flow-container">
      <VueFlow
        :nodes="nodes"
        :edges="edges"
        @nodeClick="onNodeClick"
        @edgeClick="onEdgeClick"
        @connect="onConnect"
      />
    </div>
  </main>
</template>

<script setup>
import { VueFlow } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import { ref } from 'vue'
const nodes = ref([
  {
    id: '1',
    type: 'input',
    data: { label: 'Input Node' },
    position: { x: 0, y: 0 },
  },
  {
    id: '2',
    data: { label: 'Default Node' },
    position: { x: 100, y: 100 },
  },
])

const edges = ref([
  {
    id: 'e1-2',
    source: '1',
    target: '2',
    animated: true,
  },
])

const onNodeClick = (event, node) => {
  console.log('Node clicked:', node)
}

const onEdgeClick = (event, edge) => {
  console.log('Edge clicked:', edge)
}

const onConnect = (params) => {
  console.log('Connect:', params)
}
</script>

<style scoped>
.vue-flow-container {
  width: 100%;
  height: 400px;
}
</style>