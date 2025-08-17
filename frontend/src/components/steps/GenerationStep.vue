<template>
  <main class="container">
    <h1>Generate</h1>
    <button @click="projectStore.callGenerateEndpoint">GENERATE :P</button>
    
  </main>
</template>

<script setup lang="ts">
import { useProjectStore } from "@/stores/useProjectStore"

const projectStore = useProjectStore()

</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 360px;
  min-width: 360px;
}
</style>
