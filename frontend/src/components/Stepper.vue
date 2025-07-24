<template>
  <div class="stepper">
    <div class="step-indicators">
      <div 
        v-for="(step, index) in steps" 
        :key="index"
        :class="['step', { 'active': currentStep === index, 'completed': currentStep > index }]"
        @click="goToStep(index)"
      >
        {{ index + 1 }}
      </div>
    </div>
    
    <div class="step-content">
      <component :is="steps[currentStep].component" />
    </div>
    
    <div class="step-actions">
      <button 
        v-if="currentStep > 0" 
        @click="prevStep"
        class="btn prev-btn"
      >
        Previous
      </button>
      <button 
        v-if="currentStep < steps.length - 1" 
        @click="nextStep"
        class="btn next-btn"
      >
        Next
      </button>
      <button 
        v-if="currentStep === steps.length - 1" 
        @click="finish"
        class="btn finish-btn"
      >
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
    validator: (steps) => steps.every(step => step.title && step.component)
  }
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


</style>