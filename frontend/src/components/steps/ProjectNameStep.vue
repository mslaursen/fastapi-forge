<template>
  <main class="container">
    <h1>Choose a Project Name</h1>
    <br />
    <div class="input-group">
      <div class="label-group">
        <label class="project-name-label" for="project-name">Project Name</label>
        <div class="project-name-length-indicator">{{ localProjectName.length }} / 50</div>
      </div>
      <div class="input-horizontal">
        <input
          class="project-name"
          :class="{
            confirmed: projectStore.isProjectNameConfirmed,
            'input-error': showError,
          }"
          type="text"
          placeholder="Enter your project name"
          :value="localProjectName"
          @input="handleInputChange($event)"
          :disabled="projectStore.isProjectNameConfirmed"
          maxlength="50"
        />
        <button
          class="confirm-btn"
          :class="{ confirmed: projectStore.isProjectNameConfirmed }"
          @click="handleConfirm"
          :disabled="showError || !localProjectName"
        >
          Confirm
        </button>
      </div>
      <div v-if="showError" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useProjectStore } from "@/stores/useProjectStore"

const projectStore = useProjectStore()
const localProjectName = ref("")
const showError = ref(false)
const errorMessage = ref("")

const isValidProjectName = (name) => {
  return /^[a-zA-Z_][a-zA-Z0-9_-]*$/.test(name)
}

const handleInputChange = (event) => {
  localProjectName.value = event.target.value

  if (localProjectName.value.length === 0) {
    showError.value = false
    return
  }

  if (!isValidProjectName(localProjectName.value)) {
    showError.value = true
    errorMessage.value =
      "Name must start with a letter/underscore and only contain letters, numbers, -, or _"
  } else {
    showError.value = false
  }
}

const handleConfirm = () => {
  if (projectStore.isProjectNameConfirmed) {
    projectStore.isProjectNameConfirmed = false
    projectStore.setProjectName("")
    return
  }

  if (!localProjectName.value || showError.value) return

  projectStore.setProjectName(localProjectName.value)
  projectStore.isProjectNameConfirmed = true
}

onMounted(() => {
  if (projectStore.getProjectName()) {
    localProjectName.value = projectStore.getProjectName()
  }
})
</script>

<style scoped>
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

.project-name:focus,
.project-name.confirmed {
  outline: none;
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
}
.project-name.confirmed {
  cursor: not-allowed;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  margin-bottom: 1rem;
  width: 100%;
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
.confirm-btn:hover,
.confirm-btn.confirmed {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  cursor: pointer;
  transition: 0.1s;
  background-color: var(--color-success);
}
.confirm-btn.confirmed {
  transition: 0.1s;
  background-color: var(--color-success);
}
.confirm-btn.confirmed:hover {
  background-color: var(--color-background);
  transform: translate(0px, 0px);
  box-shadow: 3px 3px 0px rgba(0, 0, 0, 1);
}
.label-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-error {
  border-color: #ff4444;
  background-color: #ffeeee;
}

.error-message {
  color: #ff4910;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-background);
}
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 360px;
  min-width: 360px;
}
</style>
