<template>
  <main class="relation-container">
    <div class="input-container">
      <div class="input-group">
        <label class="relation-label">Field name</label>
        <input class="relation-input" v-model="fieldName" type="text" />
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
        <input class="relation-input" v-model="backPopulates" type="text" />
      </div>
    </div>

    <div class="checkbox-group">
      <label><input type="checkbox" v-model="nullable" /> Nullable</label>
      <label><input type="checkbox" v-model="unique" /> Unique</label>
      <label><input type="checkbox" v-model="indexed" /> Index</label>
    </div>

    <div class="action-group">
      <button class="delete-relation-btn" @click="deleteRelation">Delete</button>
      <button class="save-relation-btn" @click="saveChanges">Save</button>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { useModalStore } from "@/stores/useModalStore"
import type { RelationalRelationField } from "@/types.types"

const props = defineProps<{
  id: string
  relation: RelationalRelationField
}>()

const projectStore = useProjectStore()
const modalStore = useModalStore()

const originalFieldName = ref("")
const fieldName = ref("")
const selectedNodeId = ref("")
const onDelete = ref("")
const backPopulates = ref("")
const nullable = ref(false)
const unique = ref(false)
const indexed = ref(false)

onMounted(() => {
  originalFieldName.value = props.relation.fieldName || ""
  fieldName.value = props.relation.fieldName || ""
  selectedNodeId.value = props.relation.targetModel || ""
  onDelete.value = props.relation.onDelete || ""
  backPopulates.value = props.relation.backPopulates || ""
  nullable.value = props.relation.isNullable || false
  unique.value = props.relation.isUnique || false
  indexed.value = props.relation.isIndex || false
})

const filteredNodes = computed(() => projectStore.nodes.filter((node) => node.id !== props.id))

const saveChanges = () => {
  if (!selectedNodeId.value || !fieldName.value) return
  projectStore.updateRelation(props.id, props.relation.targetModel, props.relation.fieldName, {
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

const deleteRelation = () => {
  projectStore.deleteRelation(props.id, props.relation.targetModel, props.relation.fieldName)
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

.delete-relation-btn {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 2px solid black;
  border-radius: 4px;
  background-color: var(--color-danger);
  box-shadow: 3px 3px 0px black;
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
}

.delete-relation-btn:hover {
  cursor: pointer;
  transform: translate(2px, 2px);
  box-shadow: none;
}
</style>
