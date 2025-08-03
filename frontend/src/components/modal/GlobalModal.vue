<template>
  <teleport to="body">
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">
            <div name="title">{{ modalTitle }}</div>
          </div>
          <div class="modal-actions" @click="close">
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
              class="lucide lucide-x h-4 w-4"
            >
              <path d="M18 6 6 18"></path>
              <path d="m6 6 12 12"></path>
            </svg>
          </div>
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
const { modalTitle, isOpen, currentComponent, props } = storeToRefs(modalStore)

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
  overflow: hidden;
  background-color: white;
  max-width: 350px;
  width: 100%;
  margin: 0 1rem;
  display: flex;
  flex-direction: column;
  background-color: var(--color-secondary);

}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
}

.modal-title {
  font-weight: bold;
  flex-grow: 1;
  display: flex;
  align-items: center;
  font-size: 1rem;
}

.modal-actions {
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  overflow: hidden;
  background-color: var(--color-secondary);
}
</style>
