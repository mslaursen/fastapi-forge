<template>
  <main class="field-modal-container">
    <div class="input-container">
      <div class="input-group">
        <label class="field-label">Field name</label>
        <input class="field-input" v-model="fieldName" type="text" maxlength="100" />
      </div>

      <div class="input-group">
        <label class="field-label">Type</label>
        <select class="field-select" v-model="type" :disabled="isPrimaryKey">
          <option disabled value="">-- Select type --</option>
          <option value="String">String</option>
          <option value="Int">Int</option>
          <option value="UUID">UUID</option>
          <option value="DateTime">DateTime</option>
          <option value="Boolean">Boolean</option>
          <option value="Float">Float</option>
          <option value="Enum">Enum</option>
        </select>
      </div>

      <div class="input-group" v-if="type === 'Enum'">
        <label class="field-label">Select Enum</label>
        <select class="field-select" v-model="selectedEnum">
          <option disabled value="">-- Select Enum --</option>
          <option v-for="e in projectStore.enums" :key="e.name" :value="e">
            {{ e.name }}
          </option>
        </select>
      </div>

      <div class="input-group">
        <label class="field-label">Default value</label>
        <select
          class="field-select"
          v-model="defaultValue"
          v-if="type === 'Enum'"
          :disabled="isPrimaryKey"
        >
          <option value="" />
          <option v-for="v in selectedEnum?.values" :key="v.name" :value="v.name">
            {{ v.name }}
          </option>
        </select>
        <input
          v-else
          class="field-input"
          v-model="defaultValue"
          type="text"
          maxlength="100"
          :disabled="isPrimaryKey || createdAtTimestamp || updatedAtTimestamp"
        />
      </div>
    </div>

    <div class="checkbox-group">
      <label><input type="checkbox" v-model="isPrimaryKey" /> Primary key</label>
      <label><input type="checkbox" v-model="isNullable" /> Nullable</label>
      <label><input type="checkbox" v-model="isUnique" /> Unique</label>
      <label><input type="checkbox" v-model="isIndex" /> Index</label>
    </div>

    <div class="checkbox-group" v-if="type === 'DateTime'">
      <label class="field-label">Timestamp</label>
      <label><input type="checkbox" v-model="createdAtTimestamp" /> Created</label>
      <label><input type="checkbox" v-model="updatedAtTimestamp" /> Updated</label>
    </div>

    <div class="action-group">
      <button class="save-field-btn" @click="saveField">Save</button>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { useModalStore } from "@/stores/useModalStore"
import type { EnumT, FieldType } from "@/types/types"
import { isValidFieldName, warningMessages } from "@/utils/validation"
import { showDangerToast } from "@/utils/toast"

const props = defineProps<{
  id: string
}>()

const projectStore = useProjectStore()
const modalStore = useModalStore()

const selectedEnum = ref<EnumT | undefined>()
const fieldName = ref("")
const type = ref("")
const defaultValue = ref("")
const isPrimaryKey = ref(false)
const isNullable = ref(false)
const isUnique = ref(false)
const isIndex = ref(false)
const metadata = ref(null)
const extraKwargs = ref({})
const createdAtTimestamp = ref(false)
const updatedAtTimestamp = ref(false)

watch(isPrimaryKey, (newVal) => {
  if (newVal) {
    type.value = "UUID"
    defaultValue.value = "uuid.uuid4"
  }
})

const resetTimestamp = () => {
  if (defaultValue.value === "datetime.now(timezone.utc)") {
    defaultValue.value = ""
  }
  extraKwargs.value = {}
}

watch(createdAtTimestamp, (newVal) => {
  if (newVal) {
    updatedAtTimestamp.value = false
    defaultValue.value = "datetime.now(timezone.utc)"
    extraKwargs.value = {}
  } else if (!updatedAtTimestamp.value) {
    resetTimestamp()
  }
})

watch(updatedAtTimestamp, (newVal) => {
  if (newVal) {
    createdAtTimestamp.value = false
    defaultValue.value = "datetime.now(timezone.utc)"
    extraKwargs.value = { onupdate: "datetime.now(timezone.utc)" }
  } else if (!createdAtTimestamp.value) {
    resetTimestamp()
  }
})

watch(type, (newVal) => {
  if (newVal === "DateTime") return
  if (createdAtTimestamp.value || updatedAtTimestamp.value) {
    resetTimestamp()
    createdAtTimestamp.value = false
    updatedAtTimestamp.value = false
  }
})

const saveField = () => {
  if (!fieldName.value || !type.value) return
  if (!isValidFieldName(fieldName.value)) {
    showDangerToast(warningMessages.fieldName)
    return
  }
  projectStore.addField(props.id, {
    name: fieldName.value,
    type: type.value as FieldType,
    typeEnum: selectedEnum.value?.name,
    isPrimaryKey: isPrimaryKey.value,
    isNullable: isNullable.value,
    isUnique: isUnique.value,
    isIndex: isIndex.value,
    defaultValue: defaultValue.value || undefined,
    metadata: metadata.value || undefined,
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
.field-input,
.field-select {
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
