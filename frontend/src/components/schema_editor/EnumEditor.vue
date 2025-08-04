<template>
  <div class="layout-container">
    <div class="enum-sidebar">
      <div class="sidebar-header">
        <div class="create-enum-wrapper">
          <input
            class="create-enum-input"
            type="text"
            placeholder="New Enum Name"
            v-model="newEnumName"
            @keyup.enter="createEnum"
          />
          <button class="create-enum-btn" @click="createEnum">+</button>
        </div>
      </div>
      <div class="enum-list">
        <div
          v-for="enumItem in enums"
          :key="enumItem.name"
          class="enum-item"
          :class="{ active: selectedEnumName === enumItem.name }"
          @click="selectEnum(enumItem)"
        >
          {{ enumItem.name }}
          <button class="delete-enum-btn" @click.stop="deleteEnum(enumItem.name)">×</button>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div v-if="selectedEnum" class="table-wrapper">
        <button
          class="delete-selected-btn"
          @click="deleteSelectedRows"
          :disabled="!hasSelectedRows"
        >
          Delete Selected
        </button>
        <table class="enum-table">
          <thead>
            <tr>
              <th>
                <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
              </th>
              <th>Name</th>
              <th>Value</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(val, index) in selectedEnum.values" :key="index">
              <td><input type="checkbox" v-model="selectedRows" :value="index" /></td>
              <td>{{ val.name }}</td>
              <td>{{ val.value }}</td>
              <td>
                <button class="action-btn">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="lucide lucide-ellipsis"
                  >
                    <circle cx="12" cy="12" r="1"></circle>
                    <circle cx="19" cy="12" r="1"></circle>
                    <circle cx="5" cy="12" r="1"></circle>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue"
import type { Enum, EnumsArray } from "@/types/types.ts"

const enums = ref<EnumsArray>([
  {
    name: "UserRole",
    values: [
      { name: "ADMIN", value: "admin" },
      { name: "USER", value: "auto()" },
    ],
  },
])

const newEnumName = ref("")
const selectedEnumName = ref<string | null>(null)

const emit = defineEmits(["enum-selected"])

const selectEnum = (enumItem: Enum) => {
  selectedEnumName.value = enumItem.name
  selectedRows.value = []
  selectAll.value = false
  emit("enum-selected", enumItem)
}

const createEnum = () => {
  if (newEnumName.value.trim() === "") return
  const newEnum: Enum = {
    name: newEnumName.value.trim(),
    values: [],
  }
  enums.value.push(newEnum)
  newEnumName.value = ""
  selectEnum(newEnum)
}

const deleteEnum = (name: string) => {
  enums.value = enums.value.filter((e: Enum) => e.name !== name)
  if (selectedEnumName.value === name) {
    selectedEnumName.value = null
    selectedRows.value = []
    selectAll.value = false
  }
}

const selectedEnum = computed(
  () => enums.value.find((e) => e.name === selectedEnumName.value) || null,
)

const selectedRows = ref<number[]>([])
const selectAll = ref(false)

const hasSelectedRows = computed(() => selectedRows.value.length > 0)

const toggleSelectAll = () => {
  if (!selectedEnum.value) return
  if (selectAll.value) {
    selectedRows.value = selectedEnum.value.values.map((_, i) => i)
  } else {
    selectedRows.value = []
  }
}

watch(selectedRows, () => {
  if (!selectedEnum.value) return
  selectAll.value = selectedRows.value.length === selectedEnum.value.values.length
})

const deleteSelectedRows = () => {
  if (!selectedEnum.value) return
  const filtered = selectedEnum.value.values.filter((_, i) => !selectedRows.value.includes(i))
  selectedEnum.value.values = filtered
  selectedRows.value = []
  selectAll.value = false
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  font-family: sans-serif;
}

.enum-sidebar {
  width: 250px;
  border-right: 2px solid black;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.sidebar-header {
  padding: 10px;
  border-bottom: 2px solid black;
}

.create-enum-wrapper {
  display: flex;
  gap: 5px;
}

.create-enum-input {
  flex: 1;
  border: 2px solid black;
  border-radius: 6px;
  padding: 4px 10px;
}

.create-enum-btn {
  width: 32px;
  border: 2px solid black;
  border-radius: 6px;
  background-color: white;
  font-weight: bold;
  cursor: pointer;
}

.create-enum-btn:hover {
  background-color: var(--color-success);
}

.enum-list {
  flex: 1;
  padding: 5px;
  overflow-y: auto;
}

.enum-item {
  padding: 10px 15px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px;
  border: 2px solid transparent;
}

.enum-item.active,
.enum-item:hover {
  background-color: var(--color-primary);
  font-weight: bold;
  border-color: black;
}

.delete-enum-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.delete-enum-btn:hover {
  color: red;
}

.main-content {
  flex: 1;
  padding: 24px;
}

.table-wrapper {
  margin-top: 20px;
}

.delete-selected-btn {
  margin-bottom: 10px;
  padding: 8px 12px;
  border: 2px solid black;
  border-radius: 8px;
  background-color: white;
  font-weight: bold;
  cursor: pointer;
}

.delete-selected-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.enum-table {
  border: 2px solid black;
  border-collapse: collapse;
  overflow: hidden;
  width: 500px;
}

.enum-table th,
.enum-table td {
  height: 25px;
  padding: 10px;
  text-align: left;
  border-bottom: 2px solid black;
}

.enum-table th:first-child,
.enum-table td:first-child {
  padding-right: 5px;
  width: 30px;
}

.enum-table th:nth-child(2),
.enum-table td:nth-child(2) {
  padding-left: 5px;
}

.enum-table th:nth-child(3),
.enum-table td:nth-child(3) {
  text-align: right;
}

.enum-table th:nth-child(4),
.enum-table td:nth-child(4) {
  width: 0px;
}

.action-btn {
  cursor: pointer;
  width: 30px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-left: 2px solid black;
  background-color: var(--color-primary);
  border-radius: 5px;
}

.action-btn:hover {
}
</style>
