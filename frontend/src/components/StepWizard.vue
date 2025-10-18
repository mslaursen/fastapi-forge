<template>
  <div class="StepWizard">
    <div class="step-indicators">
      <div
        v-for="(step, index) in steps"
        :key="index"
        :class="['step', { active: currentStep === index, completed: currentStep > index }]"
        @click="goToStep(index)"
      ></div>
    </div>

    <div class="step-content">
      <component :is="steps[currentStep]" />
    </div>

    <div class="step-actions">
      <button v-if="currentStep > 0" @click="currentStep--" class="btn prev-btn">Previous</button>
      <button v-if="currentStep < steps.length - 1" @click="nextStep" class="btn next-btn">
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"

const props = defineProps({
  steps: {
    type: Array,

    required: true,
  },
})

const currentStep = ref(0)

const nextStep = () => {
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
  }
}

const goToStep = (index) => {
  if (index >= 0 && index < props.steps.length) {
    currentStep.value = index
  }
}
</script>

<style scoped>
.StepWizard {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.step-indicators {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.step {
  caret-color: transparent;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: lightgray;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 5px;
  cursor: pointer;
  border: 2px solid black;
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 1);
  transition:
    transform 0.1s ease-out,
    box-shadow 0.1s;
}

.step:hover {
  background-color: darkgray;
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  transform: translate(2px, 2px);
}

.step.active {
  background-color: var(--color-primary);
}

.step.completed {
  background-color: var(--color-success);
}

.step-content {
  margin-bottom: 3rem;
}

.step-actions {
  display: grid;
  grid-template-rows: 1;
  grid-template-columns: 2;
  justify-content: space-between;
  width: 10%;
  position: absolute;
  bottom: 8rem;
}

.prev-btn {
  grid-column: 1;
}

.next-btn {
  grid-column: 2;
}

.next-btn,
.prev-btn,
.finish-btn {
  caret-color: transparent;
  padding: 0.5rem 1rem;
  border: 2px solid black;
  border-radius: 4px;
  background-color: var(--color-background);
  box-shadow: 3px 3px 0px rgba(0, 0, 0, 1);
  transition:
    transform 0.1s ease-in-out,
    box-shadow 0.1s;
  font-weight: bold;
}

.next-btn:hover,
.prev-btn:hover,
.finish-btn:hover {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  cursor: pointer;
}
</style>
