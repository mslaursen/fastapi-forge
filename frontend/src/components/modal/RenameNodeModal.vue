<template>
  <main class="rename-node-modal">
    <div class="input-group">
      <label class="field-label">New Node ID:</label>
      <input class="field-input" v-model="newNodeId" type="text" />
    </div>

    <button class="save-btn" @click="rename">Rename</button>
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
  gap: 1rem;
  padding: 1rem;
  border: 2px solid black;
  box-shadow: 4px 4px 0 black;
  background-color: #fff;
  width: 100%;
  max-width: 400px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.field-input {
  border: 2px solid black;
  border-radius: 4px;
  padding: 0.5rem;
  background-color: #f4f4f0;
  box-shadow: 3px 3px 0 black;
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
}

.field-input:focus {
  outline: none;
  transform: translate(2px, 2px);
  box-shadow: none;
}

.save-btn {
  align-self: flex-end;
  padding: 0.5rem 1rem;
  border: 2px solid black;
  border-radius: 4px;
  font-weight: bold;
  background-color: #2fff2f;
  box-shadow: 3px 3px 0 black;
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
