<template>
  <div class="custom-node">
    <div class="custom-node-header">
      <div class="custom-node-title">
        {{ id }}
      </div>
      <div
        class="custom-node-actions nodrag"
        @mouseover="openNodeActions"
        @mouseleave="closeNodeActions"
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
        <div class="dropdown-list" v-if="nodeActionsOpen">
          <div class="dropdown-item" @click="$emit('add-field', props.id)">Add Field</div>
          <div class="dropdown-item" @click="$emit('add-relation', props.id)">Add Relation</div>
          <div class="dropdown-item" @click="$emit('rename-node', props.id)">Rename</div>
          <div class="dropdown-item" @click="$emit('delete-node', props.id)">Delete</div>
        </div>
      </div>
    </div>
    <div class="custom-node-body nodrag">
      <div
        v-for="field in data.fields"
        :key="field.name"
        class="custom-node-field-row"
        @click="$emit('open-edit-field-modal', props.id, field)"
      >
        <div class="custom-node-field-name">{{ field.name }}</div>
        <div class="custom-node-field-type" v-if="field.type !== 'Enum'">{{ field.type }}</div>
        <div class="custom-node-field-type" v-else>{{ field.type }}({{ field.typeEnum }})</div>
      </div>
      <div
        v-for="relation in data.relations"
        :key="relation.fieldName"
        class="custom-node-field-row"
        @click="$emit('open-edit-relation-modal', props.id, relation)"
      >
        <div class="custom-node-field-name">{{ relation.fieldName }}</div>
        <div class="custom-node-field-type">{{ relation.targetModel }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
const props = defineProps<{
  id: string
  data: object
}>()

const nodeActionsOpen = ref(false)

const openNodeActions = () => {
  nodeActionsOpen.value = true
}
const closeNodeActions = () => {
  nodeActionsOpen.value = false
}
</script>

<style scoped>
.custom-node {
  border: 2px solid black;
  border-radius: 6px;
  width: 250px;
  overflow: hidden;
  background-color: white;
}

.custom-node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid black;
  width: 100%;
  height: 32px;
}

.custom-node-title {
  font-weight: bold;
  background-color: var(--color-primary);
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 8px;
}

.custom-node-actions {
  cursor: pointer;
  width: 40px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-left: 2px solid black;
  background-color: var(--color-primary);
}

.custom-node-body {
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

.custom-node-field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 28px;
  padding: 0 8px;
  border-bottom: 1px solid #e0e0e0;
}
.custom-node-field-row:hover {
  background-color: #f8f8f8;
}

.custom-node-field-row:last-child {
  border-bottom: none;
}

.custom-node-field-name {
  font-weight: 600;
  color: #343a40;
  white-space: nowrap;
  overflow: hidden;
}

.custom-node-field-type {
  font-style: italic;
  color: #6c757d;
  white-space: nowrap;
}

.dropdown-list {
  margin-left: 160px;
  caret-color: transparent;
  border: 2px solid black;
  position: absolute;
  width: 100%;
  min-width: 120px;
  max-width: 140px;
  border-radius: 5px;
  background: white;
  z-index: 100;
  padding: 4px;
  box-sizing: border-box;
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
</style>
