<template>
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
</template>

<script setup lang="ts">
import { ref } from "vue"
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
  }
}
</script>

<style scoped>
.enum-sidebar {
  width: 250px;
  height: 100%;
  border-right: 2px solid black;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.sidebar-header {
  height: 32px;
  padding: 10px;
  border-bottom: 2px solid black;
}

.create-enum-wrapper {
  display: flex;
  gap: 5px;
  height: 100%;
}

.create-enum-input {
  flex: 1;
  border: 2px solid black;
  border-radius: 6px;
  padding: 0 10px;
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
  height: 15px;
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
  padding: 0 5px;
}

.delete-enum-btn:hover {
  color: red;
}
</style>
