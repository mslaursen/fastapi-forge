<template>
  <div class="vue-flow-container">
    <div class="vue-flow-viewport">
      <div class="viewport-wrapper">
        <div class="toggle-grid-button" @click="showGrid = !showGrid">#</div>
        <VueFlow
          v-model:nodes="projectStore.nodes"
          v-model:edges="projectStore.edges"
          :default-viewport="{ zoom: 2 }"
          :max-zoom="2"
          :min-zoom="0.1"
          :fit-view-on-init="true"
        >
          <Background v-if="showGrid" variant="lines" :size="51" :gap="51" />
          <div class="create-wrapper">
            <div v-if="showInput" class="floating-create-expanded">
              <button class="collapse-btn" @click="showInput = false">
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
                  class="lucide lucide-chevron-left size-4 rdp-nav_icon"
                >
                  <path d="m15 18-6-6 6-6"></path>
                </svg>
              </button>
              <input
                class="create-model-input"
                type="text"
                placeholder="Enter Model Name"
                v-model="modelName"
                @keyup.enter="handleCreateClick"
                maxlength="100"
              />
              <button class="create-model-btn" @click="handleCreateClick">
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
                  style="height: 100%"
                >
                  <path d="M20 6 9 17l-5-5" />
                </svg>
              </button>
            </div>
            <div v-if="!showInput" class="create-circle" @click="showInput = true">+</div>
          </div>

          <template #node-custom="customNodeProps">
            <CustomNode
              v-bind="customNodeProps"
              @delete-node="deleteNode"
              @rename-node="openRenameNodeModal"
              @add-field="openAddFieldModal"
              @add-relation="openAddRelationModal"
              @open-edit-field-modal="openEditFieldModal"
              @open-edit-relation-modal="openEditRelationModal"
            />
          </template>
        </VueFlow>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import CustomNode from "@/components/schema_editor/CustomNode.vue"
import "@vue-flow/core/dist/style.css"
import AddFieldModal from "@/components/modal/AddFieldModal.vue"
import EditFieldModal from "@/components/modal/EditFieldModal.vue"
import EditRelationModal from "@/components/modal/EditRelationModal.vue"
import AddRelationModal from "@/components/modal/AddRelationModal.vue"
import RenameNodeModal from "@/components/modal/RenameNodeModal.vue"
import { useProjectStore } from "@/stores/useProjectStore"
import { VueFlow } from "@vue-flow/core"
import { useModalStore } from "@/stores/useModalStore"
import type { RelationalRelationField, RelationalField } from "@/types.types"
import { Background } from "@vue-flow/background"
import { isValidModelName, warningMessages } from "@/utils/validation"
import { showDangerToast } from "@/utils/toast"

const projectStore = useProjectStore()
const modalStore = useModalStore()

const modelName = ref("")
const showInput = ref(false)
const showGrid = ref(true)

const handleCreateClick = () => {
  const newModelName = modelName.value.trim()
  if (newModelName === "") return
  if (!isValidModelName(newModelName)) {
    showDangerToast(warningMessages.modelName)
    return
  }
  projectStore.createNode(newModelName)
  modelName.value = ""
  showInput.value = false
}

const deleteNode = (id: string) => {
  projectStore.deleteNode(id)
}

const openRenameNodeModal = (id: string) => {
  modalStore.open(id, RenameNodeModal, { id })
}

const openAddFieldModal = (id: string) => {
  modalStore.open(id, AddFieldModal, { id })
}

const openEditFieldModal = (id: string, field: RelationalField) => {
  modalStore.open("Edit field", EditFieldModal, { id, field })
}

const openAddRelationModal = (id: string) => {
  modalStore.open(id, AddRelationModal, { id })
}

const openEditRelationModal = (id: string, relation: RelationalRelationField) => {
  modalStore.open(relation.fieldName, EditRelationModal, { id, relation })
}
</script>

<style scoped>
.vue-flow-container {
  height: 100%;
  display: flex;
}

.vue-flow-viewport {
  position: relative;
  flex: 1;
  display: flex;
}

.viewport-wrapper {
  width: 100%;
  height: 100%;
}

.toggle-grid-button {
  caret-color: transparent;
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--color-primary);
  color: black;
  border: 2px solid black;
  padding: 3px 6px;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
  z-index: 10;
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 1);
}

.toggle-grid-button:hover {
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  transform: translate(2px, 2px);
}

.create-wrapper {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
}

.create-circle {
  width: 40px;
  height: 40px;
  background-color: var(--color-primary);
  border: 2px solid black;
  color: black;
  border-radius: 50%;
  font-size: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  user-select: none;
  font-weight: bold;
  z-index: 10;
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 1);
}

.create-circle:hover {
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  transform: translate(2px, 2px);
}

.floating-create-expanded {
  display: flex;
  align-items: center;
  background: var(--color-primary);
  border: 2px solid black;
  border-radius: 50px;
  height: 40px;
  padding: 0 10px;
  gap: 8px;
  z-index: 1000;
  margin-top: 2px;
  margin-left: 2px;
}

.collapse-btn {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  padding: 0;
  cursor: pointer;
  background: none;
  border: none;
}

.collapse-btn svg {
  width: 20px;
  height: 20px;
}

.create-model-input {
  height: 26px;
  border: 2px solid black;
  border-radius: 6px;
  padding: 0 10px;
  width: 160px;
}

.create-model-btn {
  height: 30px;
  border: 2px solid black;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  background-color: var(--color-secondary);
  margin-right: 5px;
}

.create-model-btn:hover {
  background-color: var(--color-success);
}
</style>
