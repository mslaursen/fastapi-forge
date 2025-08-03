<template>
  <main class="relation-container">
    <div class="grid-2x2">
      <div class="input-group">
        <label class="relation-label">Field Name:</label>
        <input class="relation-input" v-model="fieldName" type="text" />
      </div>

      <div class="input-group">
        <label class="relation-label">Target Model:</label>
        <select class="relation-select" v-model="selectedNodeId">
          <option disabled value="">-- Select a model --</option>
          <option v-for="node in filteredNodes" :key="node.id" :value="node.id">
            {{ node.id }}
          </option>
        </select>
      </div>

      <div class="input-group">
        <label class="relation-label">OnDelete:</label>
        <select class="relation-select" v-model="onDelete">
          <option disabled value="">-- Select behavior --</option>
          <option value="CASCADE">CASCADE</option>
          <option value="SET_NULL">SET_NULL</option>
        </select>
      </div>

      <div class="input-group">
        <label class="relation-label">Back Populates:</label>
        <input class="relation-input" v-model="backPopulates" type="text" />
      </div>
    </div>

    <div class="checkbox-group">
      <label><input type="checkbox" v-model="nullable" /> Nullable</label>
      <label><input type="checkbox" v-model="unique" /> Unique</label>
      <label><input type="checkbox" v-model="indexed" /> Index</label>
    </div>

    <button class="save-relation-btn" @click="saveSelect">Save</button>
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { useModalStore } from "@/stores/useModalStore"

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

  projectStore.addRelation(props.id, selectedNodeId.value, {
    fieldName: fieldName.value,
    targetModel: selectedNodeId.value,
    backPopulates: backPopulates.value,
    onDelete: onDelete.value,
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
  border: 2px solid black;
  padding: 1rem;
  box-shadow: 4px 4px 0px black;
  background-color: #fff;
}

.grid-2x2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.relation-label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.relation-input,
.relation-select {
  border: 2px solid black;
  border-radius: 4px;
  padding: 0.5rem;
  box-shadow: 3px 3px 0px black;
  background-color: var(--color-background);
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
}

.relation-input:focus,
.relation-select:focus {
  outline: none;
  transform: translate(2px, 2px);
  box-shadow: none;
}

.checkbox-group {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-weight: bold;
}

.save-relation-btn {
  align-self: flex-end;
  padding: 0.5rem 1rem;
  border: 2px solid black;
  border-radius: 4px;
  font-weight: bold;
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
