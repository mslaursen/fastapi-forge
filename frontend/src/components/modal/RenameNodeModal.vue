<template>
  <main class="rename-node-modal">
    <div class="input-container">
      <div class="input-group">
        <label class="field-label">New model name</label>
        <input class="field-input" v-model="newNodeId" type="text" />
      </div>
    </div>

    <div class="action-group">
      <button class="save-btn" @click="rename">Rename</button>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { useModalStore } from "@/stores/useModalStore"

const props = defineProps<{
  id: string
}>()

const projectStore = useProjectStore()
const modalStore = useModalStore()

const newNodeId = ref(props.id)

const rename = () => {
  if (!newNodeId.value.trim() || newNodeId.value === props.id) {
    modalStore.close()
    return
  }

  projectStore.renameNode(props.id, newNodeId.value.trim())
  modalStore.close()
}
</script>

<style scoped>
.rename-node-modal {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.input-container {
  display: flex;
  flex-direction: column;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-weight: bold;
  margin-bottom: 5px;
}

.field-input {
  border: 2px solid black;
  border-radius: 6px;
  padding: 0.6rem;
  background-color: white;
}

.action-group {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
}

.save-btn {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 2px solid black;
  border-radius: 4px;
  background-color: var(--color-success);
  box-shadow: 3px 3px 0px black;
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
}

.save-btn:hover {
  cursor: pointer;
  transform: translate(2px, 2px);
  box-shadow: none;
}
</style>
