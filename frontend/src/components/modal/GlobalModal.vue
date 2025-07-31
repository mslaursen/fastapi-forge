<template>
  <teleport to="body">
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">
            <slot name="title">Modal Title</slot>
          </div>
          <div class="modal-actions" @click="close">×</div>
        </div>
        <div class="modal-body">
          <component v-if="currentComponent" :is="currentComponent" v-bind="props" @close="close" />
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { storeToRefs } from "pinia"
import { useModalStore } from "@/stores/useModalStore"

const modalStore = useModalStore()
const { isOpen, currentComponent, props } = storeToRefs(modalStore)

function close() {
  modalStore.close()
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  border: 2px solid black;
  border-radius: 6px;
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 1);
  overflow: hidden;
  background-color: white;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid black;
  width: 100%;
  height: 32px;
}

.modal-title {
  font-weight: bold;
  background-color: #ffdb58;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
}

.modal-actions {
  cursor: pointer;
  width: 32px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-left: 2px solid black;
  font-size: 1.2rem;
}

.modal-actions:hover {
  background-color: #f0f0f0;
}

.modal-body {
  display: flex;
  flex-direction: column;
  padding: 0;
}
</style>
