<template>
  <main class="relation-container">
    <div class="input-container">
      <div class="input-group">
        <label class="relation-label">Field name</label>
        <input class="relation-input" v-model="fieldName" type="text" maxlength="100" />
      </div>

      <div class="input-group">
        <label class="relation-label">Target model</label>
        <select class="relation-select" v-model="selectedNodeId">
          <option disabled value="">-- Select a model --</option>
          <option v-for="node in filteredNodes" :key="node.id" :value="node.id">
            {{ node.id }}
          </option>
        </select>
      </div>

      <div class="input-group">
        <label class="relation-label">OnDelete</label>
        <select class="relation-select" v-model="onDelete">
          <option disabled value="">-- Select behavior --</option>
          <option value="CASCADE">CASCADE</option>
          <option value="SET_NULL">SET_NULL</option>
        </select>
      </div>

      <div class="input-group">
        <label class="relation-label">Back populates</label>
        <input class="relation-input" v-model="backPopulates" type="text" maxlength="100" />
      </div>
    </div>

    <div class="checkbox-group">
      <label><input type="checkbox" v-model="nullable" /> Nullable</label>
      <label><input type="checkbox" v-model="unique" /> Unique</label>
      <label><input type="checkbox" v-model="indexed" /> Index</label>
    </div>

    <div class="action-group">
      <button class="save-relation-btn" @click="saveSelect">Save</button>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { useModalStore } from "@/stores/useModalStore"
import type { OnDeleteType } from "@/types/types"
import { isValidFieldName, warningMessages } from "@/utils/validation"
import { showDangerToast } from "@/utils/toast"

const props = defineProps<{
  id: string
}>()

const projectStore = useProjectStore()
const modalStore = useModalStore()

const fieldName = ref("")
const selectedNodeId = ref("")
const onDelete = ref("")
const backPopulates = ref("")
const nullable = ref(false)
const unique = ref(false)
const indexed = ref(false)

const filteredNodes = computed(() => projectStore.nodes.filter((node) => node.id !== props.id))

const saveSelect = () => {
  if (!selectedNodeId.value || !fieldName.value) return
  if (!isValidFieldName(fieldName.value)) {
    showDangerToast(warningMessages.fieldName)
    return
  }
  projectStore.addRelation(props.id, selectedNodeId.value, {
    fieldName: fieldName.value,
    targetModel: selectedNodeId.value,
    backPopulates: backPopulates.value,
    onDelete: onDelete.value as OnDeleteType,
    isNullable: nullable.value,
    isUnique: unique.value,
    isIndex: indexed.value,
  })
  modalStore.close()
}
</script>

<style scoped>
.relation-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.relation-label {
  font-weight: bold;
  margin-bottom: 5px;
}

.relation-input,
.relation-select {
  border: 2px solid black;
  border-radius: 6px;
  padding: 0.6rem;
  background-color: white;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-weight: bold;
}

.action-group {
  gap: 0.5rem;
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
}

.save-relation-btn {
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

.save-relation-btn:hover {
  cursor: pointer;
  transform: translate(2px, 2px);
  box-shadow: none;
}
</style>
