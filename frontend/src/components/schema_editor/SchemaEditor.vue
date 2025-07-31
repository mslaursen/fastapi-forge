<template>
  <main class="container">
    <div class="vue-flow-container">
      <div class="vue-flow-header">
        <div class="vue-flow-create-model">
          <input
            class="create-model-input"
            type="text"
            placeholder="Enter Model Name"
            v-model="modelName"
          />
          <button class="create-model-btn" @click="createNode">Create</button>
        </div>
      </div>

      <div class="vue-flow-viewport">
        <VueFlow v-model:nodes="store.nodes" v-model:edges="store.edges">
          <template #node-custom="customNodeProps">
            <CustomNode
              v-bind="customNodeProps"
              @delete-node="deleteNode"
              @add-field="openAddFieldModal"
              @add-relation="openAddRelationModal"
              @open-edit-field-modal="openEditFieldModal"
              @open-edit-relation-modal="openEditRelationModal"
            />
          </template>
        </VueFlow>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue"
import CustomNode from "@/components/schema_editor/CustomNode.vue"
import "@vue-flow/core/dist/style.css"
import AppModal from "@/components/modal/AppModal.vue"
import AddFieldModal from "@/components/modal/AddFieldModal.vue"
import EditFieldModal from "@/components/modal/EditFieldModal.vue"
import EditRelationModal from "@/components/modal/EditRelationModal.vue"
import AddRelationModal from "@/components/modal/AddRelationModal.vue"
import { useProjectStore } from "@/stores/store"
import { VueFlow } from "@vue-flow/core"
import { useModalStore } from "@/stores/useModalStore"
import type { RelationalRelationField } from "@/types.types"

const store = useProjectStore()
const modalStore = useModalStore()

const modelName = ref("")

const createNode = () => {
  if (modelName.value.trim() === "") return
  store.createNode(modelName.value)
  modelName.value = ""
}

const deleteNode = (id: string) => {
  store.deleteNode(id)
}

const openAddFieldModal = (id: string) => {
  modalStore.open(AddFieldModal, { id })
}

const openEditFieldModal = (id: string, field: object) => {
  modalStore.open(EditFieldModal, { id, field })
}

const openAddRelationModal = (id: string) => {
  modalStore.open(AddRelationModal, { id })
}

const openEditRelationModal = (id: string, relation: RelationalRelationField) => {
  modalStore.open(EditRelationModal, { id, relation })
  console.log(relation, id)
}
</script>

<style scoped>
.container {
  width: 100%;
  height: 100%;
}
.vue-flow-container {
  width: 1000px;
  height: 500px;
  border: 2px solid black;
  border-radius: 6px;
}
.vue-flow-header {
  height: 40px;
  border-bottom: 2px solid black;
  display: flex;
  align-items: center;
  padding: 0 5px;
  background-color: #ffdb58;
}

.vue-flow-viewport {
  width: 100%;
  height: calc(100% - 35px);
}

.vue-flow-create-model {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  width: 300px;
}

.create-model-input {
  width: 100%;
  height: 12px;
  padding: 0.5rem;
  border: 2px solid black;
  border-radius: 4px;
}
.create-model-input:focus {
  outline: none;
}

.create-model-btn {
  caret-color: transparent;
  border: 2px solid black;
  border-radius: 4px;
  background-color: #f4f4f0;
  padding: 0.25rem;
  height: 32px;
  font-weight: bold;
}

.create-model-btn:hover {
  cursor: pointer;
  transition: 0.1s;
  background-color: #2fff2f;
}
</style>
