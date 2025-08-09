<template>
  <main class="field-modal-container">
    <div class="input-container">
      <div class="input-group">
        <label class="field-label">Name</label>
        <input class="field-input" v-model="name" type="text" maxlength="100" />
      </div>

      <div class="input-group">
        <label class="field-label">Value</label>
        <input class="field-input" v-model="value" type="text" maxlength="100" />
      </div>
    </div>

    <div class="action-group">
      <button class="save-field-btn" @click="saveEnumValue">Save</button>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { useModalStore } from "@/stores/useModalStore"
import type { EnumValue } from "@/types/types"
import { isValidEnumValueName, warningMessages } from "@/utils/validation"
import { showDangerToast } from "@/utils/toast"

const props = defineProps<{
  enumName: string
  enumValue: EnumValue
}>()

const projectStore = useProjectStore()
const modalStore = useModalStore()

const name = ref(props.enumValue.name)
const value = ref(props.enumValue.value)

const saveEnumValue = () => {
  if (!isValidEnumValueName(name.value)) {
    showDangerToast(warningMessages.enumValueName)
    return
  }
  projectStore.updateEnumValue(props.enumName, props.enumValue.name, {
    name: name.value,
    value: value.value,
  })
  modalStore.close()
}
</script>

<style scoped>
.field-modal-container {
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
  gap: 0.5rem;
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
}

.save-field-btn {
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

.save-field-btn:hover {
  cursor: pointer;
  transform: translate(2px, 2px);
  box-shadow: none;
}
</style>

function showDangerToast(modelName: any) { throw new Error("Function not implemented."); }
