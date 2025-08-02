<template>
  <main class="container">
    <h1>Choose a Database</h1>
    <br />
    <div class="db-grid-container">
      <div class="db-grid">
        <div
          class="db-item"
          v-for="db in databases"
          :key="db"
          :class="{
            confirmed: projectStore.getDatabase() === db,
            disabled: db !== 'PostgreSQL',
            enabled: db === 'PostgreSQL',
          }"
          @click="handleDatabaseClick(db)"
        >
          <span>{{ db }}</span>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { onMounted } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"

const projectStore = useProjectStore()
const databases = ["PostgreSQL", "MySQL", "SQLite"]

const handleDatabaseClick = (db) => {
  if (db !== "PostgreSQL") return
  projectStore.setDatabase(projectStore.getDatabase() === db ? "" : db)
}

onMounted(() => {
  if (projectStore.getDatabase() && projectStore.getDatabase() !== "PostgreSQL") {
    projectStore.setDatabase("")
  }
})
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

.db-grid-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.db-grid {
  display: grid;
  grid-template-columns: repeat(3, 100px);
  gap: 3rem;
  justify-items: center;
}

.db-item {
  caret-color: transparent;
  border: 2px solid black;
  font-weight: bold;
  border-radius: 4px;
  box-shadow: 3px 3px 0px rgba(0, 0, 0, 1);
  padding: 1rem;
  text-align: center;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f4f4f0;
  transition: all 0.1s ease-in-out;
}

.db-item.enabled:hover {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  cursor: pointer;
  background-color: #2fff2f;
}

.db-item.enabled.confirmed {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  background-color: #2fff2f;
}

.db-item.enabled.confirmed:hover {
  background-color: #f4f4f0;
  transform: translate(0px, 0px);
  box-shadow: 3px 3px 0px rgba(0, 0, 0, 1);
}

.db-item.disabled {
  opacity: 0.6;
  background-color: #e0e0e0;
  cursor: not-allowed;
  box-shadow: none;
}

.db-item.disabled:hover {
  transform: none;
  box-shadow: none;
}
</style>
