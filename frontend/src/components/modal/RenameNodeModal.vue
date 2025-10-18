<template>
  <main class="rename-node-modal">
    <div class="input-container">
      <div class="input-group">
        <label class="field-label">New model name</label>
        <input class="field-input" v-model="nodeId" type="text" maxlength="100" />
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
import { isValidModelName, warningMessages } from "@/utils/validation"
import { showDangerToast } from "@/utils/toast"

const props = defineProps<{
  id: string
}>()

const projectStore = useProjectStore()
const modalStore = useModalStore()

const nodeId = ref(props.id)

const rename = () => {
  const newNodeId = nodeId.value.trim()
  if (!isValidModelName(newNodeId)) {
    showDangerToast(warningMessages.modelName)
    return
  }
  if (!newNodeId || nodeId.value === props.id) {
    modalStore.close()
    return
  }

  projectStore.renameNode(props.id, newNodeId)
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
