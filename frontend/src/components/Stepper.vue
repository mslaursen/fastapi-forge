<template>
  <div class="stepper">
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
      <button v-if="currentStep > 0" @click="prevStep" class="btn prev-btn">Previous</button>
      <button v-if="currentStep < steps.length - 1" @click="nextStep" class="btn next-btn">
        Next
      </button>
      <button v-if="currentStep === steps.length - 1" @click="finish" class="btn finish-btn">
        Finish
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  steps: {
    type: Array,

    required: true,
  },
})

const emit = defineEmits(['completed'])

const currentStep = ref(0)

const nextStep = () => {
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const goToStep = (index) => {
  if (index >= 0 && index < props.steps.length) {
    currentStep.value = index
  }
}

const finish = () => {
  emit('completed')
}
</script>

<style scoped>
.stepper {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.step-indicators {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}
.step {
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
}

.step:hover {
  background-color: darkgray;
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 1);
}

.step.active {
  background-color: #ffdb58;
}

.step.completed {
  background-color: #7fbc8c;
}

.step-content {
  margin-bottom: 1rem;
}
</style>