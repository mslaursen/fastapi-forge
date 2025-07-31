<template>
  <main class="field-modal-container">
    <div class="grid-2x2">
      <div class="input-group">
        <label class="field-label">Field Name:</label>
        <input class="field-input" v-model="fieldName" type="text" />
      </div>

      <div class="input-group">
        <label class="field-label">Type:</label>
        <select class="field-select" v-model="type">
          <option disabled value="">-- Select type --</option>
          <option value="String">String</option>
          <option value="Int">Int</option>
          <option value="UUID">UUID</option>
          <option value="DateTime">DateTime</option>
          <option value="Boolean">Boolean</option>
          <option value="Float">Float</option>
        </select>
      </div>

      <div class="input-group">
        <label class="field-label">Default Value:</label>
        <input class="field-input" v-model="defaultValue" type="text" />
      </div>

      <div class="input-group checkbox-inline">
        <label class="field-label">Primary Key:</label>
        <input type="checkbox" v-model="isPrimaryKey" />
      </div>
    </div>

    <div class="checkbox-group">
      <label><input type="checkbox" v-model="isNullable" /> Nullable</label>
      <label><input type="checkbox" v-model="isUnique" /> Unique</label>
      <label><input type="checkbox" v-model="isIndex" /> Index</label>
    </div>

    <button class="save-field-btn" @click="saveField">Save</button>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useProjectStore } from "@/stores/store"
import { useModalStore } from "@/stores/useModalStore"
import type { Field } from "@/types/types"

const props = defineProps<{
  id: string
  field: Field
}>()

const store = useProjectStore()
const modalStore = useModalStore()

const fieldName = ref(props.field.name)
const type = ref(props.field.type)
const defaultValue = ref(props.field.default || "")
const isPrimaryKey = ref(props.field.isPrimaryKey || false)
const isNullable = ref(props.field.isNullable || false)
const isUnique = ref(props.field.isUnique || false)
const isIndex = ref(props.field.isIndex || false)

const saveField = () => {
  const node = store.nodes.find((n) => n.id === props.id)
  if (!node || !node.data?.fields) return

  const fieldIndex = node.data.fields.findIndex((f) => f.name === props.field.name)
  if (fieldIndex === -1) return

  node.data.fields[fieldIndex] = {
    name: fieldName.value,
    type: type.value,
    default: defaultValue.value || undefined,
    isPrimaryKey: isPrimaryKey.value,
    isNullable: isNullable.value,
    isUnique: isUnique.value,
    isIndex: isIndex.value,
  }

  modalStore.close()
}
</script>

<style scoped>
.field-modal-container {
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

.checkbox-inline {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.field-label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.field-input,
.field-select {
  border: 2px solid black;
  border-radius: 4px;
  padding: 0.5rem;
  box-shadow: 3px 3px 0px black;
  background-color: #f4f4f0;
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
}

.field-input:focus,
.field-select:focus {
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

.save-field-btn {
  align-self: flex-end;
  padding: 0.5rem 1rem;
  border: 2px solid black;
  border-radius: 4px;
  font-weight: bold;
  background-color: #2fff2f;
  box-shadow: 3px 3px 0px black;
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
}

.save-field-btn:hover {
  cursor: pointer;
  transform: translate(2px, 2px);
  box-shadow: none;
}
</style>
