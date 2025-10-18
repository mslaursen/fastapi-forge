<template>
  <main class="container">
    <h1>Design your Schema</h1>
    <br />
    <div>
      <Viewport />
    </div>
  </main>
</template>

<script setup lang="ts">
import Viewport from "@/components/schema_editor/Viewport.vue"
</script>

<style scoped>
.container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}
</style>
