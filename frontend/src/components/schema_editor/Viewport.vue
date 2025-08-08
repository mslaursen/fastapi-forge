<template>
  <main class="container">
    <div class="editor-container">
      <div class="editor-header">
        <div
          class="header-section"
          :class="{ active: activeTab === 'models' }"
          @click="activeTab = 'models'"
        >
          Models
        </div>
        <div class="header-divider" />
        <div
          class="header-section"
          :class="{ active: activeTab === 'enums' }"
          @click="activeTab = 'enums'"
        >
          Enums
        </div>
      </div>

      <div class="editor-content">
        <SchemaEditor v-if="activeTab === 'models'" />
        <EnumEditor v-if="activeTab === 'enums'" />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue"
import SchemaEditor from "@/components/schema_editor/SchemaEditor.vue"
import EnumEditor from "@/components/schema_editor/EnumEditor.vue"

const activeTab = ref<"models" | "enums">("models")
</script>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
}

.editor-container {
  width: 1000px;
  height: 500px;
  background-color: #ffffff;
  border: 2px solid black;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-header {
  height: 40px;
  display: flex;
  align-items: center;
  background-color: var(--color-primary);
  width: 100%;
  border-bottom: 2px solid black;
  box-sizing: border-box;
}

.header-section {
  flex: 1;
  text-align: center;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  user-select: none;
}

.header-divider {
  width: 2px;
  height: 100%;
  background-color: black;
}

.editor-content {
  position: relative;
  flex: 1;
  width: 100%;
  height: calc(100% - 40px);
}
</style>
