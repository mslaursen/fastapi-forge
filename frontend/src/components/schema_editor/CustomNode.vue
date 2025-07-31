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
        >
        <div class="custom-node-actions-content" v-if="nodeActionsOpen">
          <div class="custom-node-actions-content-action" @click="$emit('add-field', props.id)">
            Add Field
          </div>
          <div class="custom-node-actions-content-action" @click="$emit('add-relation', props.id)">
            Add Relation
          </div>
          <div class="custom-node-actions-content-action" @click="$emit('delete-node', props.id)">
            Delete
          </div>
        </div>
      </div>
    </div>
    <div class="custom-node-body nodrag">
      <div
        v-for="field in data.fields"
        :key="field.name"
        class="custom-node-field-row"
        :class="{ 'primary-key': field.isPrimaryKey }"
        @click="$emit('open-edit-field-modal', props.id, field)"
      >
        <div class="custom-node-field-name">{{ field.name }}</div>
        <div class="custom-node-field-type">{{ field.type }}</div>
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
import type { Position2D } from "@/types/types"
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
.custom-node-actions-content {
  position: absolute;
  background-color: #ffffff;
  border: 2px solid black;
  border-radius: 4px;
  padding: 4px;
  z-index: 10;
  margin-left: 160px;
  width: 120px;
}
.custom-node-actions-content-action {
  cursor: pointer;
}

.custom-node {
  border: 2px solid black;
  border-radius: 6px;
  width: 250px;
  overflow: hidden;
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
  background-color: #ffdb58;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
}

.custom-node-actions {
  cursor: pointer;
  width: 32px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-left: 2px solid black;
}

.custom-node-actions:hover {
  background-color: #f0f0f0;
}

.custom-node-body {
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
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

.custom-node-field-row.primary-key {
  background-color: #90ee90;
}
.custom-node-field-row.primary-key:hover {
  background-color: #f8f8f8;
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
</style>
