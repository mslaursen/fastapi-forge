<template>
  <div class="layout-container">
    <div class="enum-sidebar">
      <div class="sidebar-header">
        <div class="input-group">
          <div class="input-horizontal">
            <input
              id="new-enum-name"
              class="project-name"
              type="text"
              placeholder="Enter new enum name"
              v-model="newEnumName"
              @keyup.enter="createEnum"
              maxlength="50"
            />
            <button class="confirm-btn" @click="createEnum" :disabled="!newEnumName">
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
                class="lucide lucide-check"
              >
                <path d="M20 6 9 17l-5-5" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      <div class="enum-list">
        <div
          v-for="enumItem in projectStore.enums"
          :key="enumItem.name"
          class="enum-item"
          :class="{ active: selectedEnum?.name === enumItem.name }"
          @click="selectEnum(enumItem)"
        >
          <div class="enum-name-wrapper">
            <span v-if="!isEditingEnumItem(enumItem)">{{ enumItem.name }}</span>
            <input
              v-else
              type="text"
              class="enum-name-edit-input"
              v-model="editedEnumName"
              @click.stop
              @keyup.enter="handleEditToggle(enumItem)"
              ref="enumNameInput"
            />
          </div>
          <div class="enum-item-actions">
            <button class="edit-enum-toggle-btn" @click.stop="handleEditToggle(enumItem)">
              <span v-if="isEditingEnumItem(enumItem)">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-save"
                >
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                  <path d="M17 21v-8H7v8" />
                  <path d="M7 3v4h6" />
                </svg>
              </span>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-pencil"
              >
                <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                <path d="m15 5 4 4" />
              </svg>
            </button>
            <button class="delete-enum-btn" @click.stop="deleteEnum(enumItem)">×</button>
          </div>
        </div>
      </div>
    </div>
    <div class="main-content" v-if="selectedEnum">
      <table class="main-table">
        <thead>
          <tr>
            <th class="name-column">Name</th>
            <th class="value-column">Value</th>
            <th class="action-column">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(ev, index) in selectedEnum.values" :key="index">
            <td class="name-column">{{ ev.name }}</td>
            <td class="value-column">{{ ev.value }}</td>
            <td class="action-column">
              <div class="action-content">
                <div
                  class="enum-actions"
                  @mouseover="openActions(index)"
                  @mouseleave="closeActions(index)"
                >
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
                  <div class="dropdown-list" v-if="activeActionIndex === index">
                    <div class="dropdown-item" @click="openEditEnumValueModal(ev)">Edit</div>
                    <div class="dropdown-item" @click="handleDeleteEnumValue(ev)">Delete</div>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="main-footer">
        <button class="add-btn" @click="openAddEnumValueModal">Add Enum Value</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { useModalStore } from "@/stores/useModalStore"
import AddEnumValueModal from "@/components/modal/AddEnumValueModal.vue"
import EditEnumValueModal from "@/components/modal/EditEnumValueModal.vue"
import type { EnumT, EnumValue } from "@/types/types"

const projectStore = useProjectStore()
const modalStore = useModalStore()

const newEnumName = ref("")
const selectedEnum = ref<EnumT | null>(null)
const editingEnumName = ref<string | null>(null)
const editedEnumName = ref("")
const activeActionIndex = ref<number | null>(null)
const enumNameInput = ref<HTMLInputElement | null>(null)

const openAddEnumValueModal = () => {
  const e = selectedEnum.value
  if (!e) return
  modalStore.open("Add Enum Value", AddEnumValueModal, { enumName: e.name })
}

const openEditEnumValueModal = (enumValue: EnumValue) => {
  const e = selectedEnum.value
  if (!e) return
  modalStore.open("Edit Enum Value", EditEnumValueModal, { enumName: e.name, enumValue: enumValue })
}

const handleDeleteEnumValue = (enumValue: EnumValue) => {
  console.log("Delete enum value:", enumValue)
}

const selectEnum = (e: EnumT) => {
  selectedEnum.value = e
}

const createEnum = () => {
  const name = newEnumName.value.trim()
  if (name === "") return
  const newEnum = projectStore.addEnum(name)
  newEnumName.value = ""
  selectEnum(newEnum)
}

const deleteEnum = (e: EnumT) => {
  projectStore.deleteEnum(e.name)
  if (selectedEnum.value?.name === e.name) {
    selectedEnum.value = null
  }
}

const isEditingEnumItem = (enumItem: EnumT) => {
  return editingEnumName.value === enumItem.name
}

const handleEditToggle = (enumItem: EnumT) => {
  if (isEditingEnumItem(enumItem)) {
    saveEnumName(enumItem)
  } else {
    editingEnumName.value = enumItem.name
    editedEnumName.value = enumItem.name
    nextTick(() => {
      if (enumNameInput.value) {
        enumNameInput.value.focus()
      }
    })
  }
}

const saveEnumName = (enumItem: EnumT) => {
  const newName = editedEnumName.value.trim()
  if (newName && newName !== enumItem.name) {
    projectStore.updateEnumName(enumItem.name, newName)
    if (selectedEnum.value?.name === enumItem.name) {
      selectedEnum.value.name = newName
    }
  }
  editingEnumName.value = null
  editedEnumName.value = ""
}

const openActions = (index: number) => {
  activeActionIndex.value = index
}

const closeActions = (index: number) => {
  if (activeActionIndex.value === index) {
    activeActionIndex.value = null
  }
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100%;
  min-height: 0;
}
.enum-sidebar {
  width: 250px;
  border-right: 2px solid black;
  display: flex;
  flex-direction: column;
  background-color: white;
}
.sidebar-header {
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
.enum-name-wrapper {
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-right: 8px;
}
.enum-name-edit-input {
  width: 100%;
  background: none;
  border: 2px solid black;
  border-radius: 4px;
  padding: 2px 5px;
  box-sizing: border-box;
  background-color: white;
}
.enum-item-actions {
  display: flex;
  gap: 0;
  align-items: center;
}
.edit-enum-toggle-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}
.edit-enum-toggle-btn:hover {
  color: var(--color-success);
}
.delete-enum-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.delete-enum-btn:hover {
  color: red;
}
.main-header {
  height: 50px;
  border-bottom: 2px solid black;
  position: sticky;
  top: 0;
  background-color: inherit;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 15px;
}
.enum-title {
  font-size: 1.2rem;
  font-weight: bold;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
.main-table {
  width: 100%;
  border-collapse: collapse;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}
.main-table thead {
  display: table;
  width: 100%;
  table-layout: fixed;
}
.main-table tbody {
  display: block;
  overflow-y: auto;
  flex: 1;
  width: 100%;
}
.main-table tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}
.main-table th,
.main-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 2px solid black;
}
.name-column {
}
.value-column {
}
.action-column {
  width: 20%;
  text-align: right !important;
}
.action-content {
  margin-right: 15px;
}
.enum-actions {
  cursor: pointer;
  display: flex;
  justify-content: flex-end;
  position: relative;
}
.dropdown-list {
  position: absolute;
  border: 2px solid black;
  border-radius: 5px;
  background: white;
  z-index: 100;
  padding: 4px;
  left: 0;
  min-width: 100px;
}
.dropdown-item {
  height: 35px;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0 5px;
  box-sizing: border-box;
  border: 2px solid transparent;
  border-radius: 5px;
}
.dropdown-item:hover {
  border: 2px solid black;
  cursor: pointer;
}
.main-footer {
  height: 50px;
  border-top: 2px solid black;
  position: sticky;
  bottom: 0;
  padding: 0 15px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 10px;
}
.project-name-label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}
.input-horizontal {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.confirm-btn {
  caret-color: transparent;
  border: 2px solid black;
  border-radius: 4px;
  background-color: var(--color-background);
  padding: 0.25rem;
  box-shadow: 3px 3px 0px rgba(0, 0, 0, 1);
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
  height: 2.125rem;
  font-weight: bold;
}
.confirm-btn:hover {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  cursor: pointer;
  transition: 0.1s;
  background-color: var(--color-success);
}
.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-background);
}
.project-name {
  width: 100%;
  padding: 0.5rem;
  border: 2px solid black;
  border-radius: 4px;
  box-shadow: 3px 3px 0px rgba(0, 0, 0, 1);
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
}
.project-name:focus {
  outline: none;
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
}
.label-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.add-btn {
  caret-color: transparent;
  border: 2px solid black;
  border-radius: 4px;
  background-color: var(--color-success);
  padding: 0.5rem 1rem;
  box-shadow: 3px 3px 0px rgba(0, 0, 0, 1);
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s ease-in-out;
  font-weight: bold;
}
.add-btn:hover {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  cursor: pointer;
  transition: 0.1s;
}
</style>
