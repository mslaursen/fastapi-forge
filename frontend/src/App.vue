<template>
  <div id="app">
    <h1>My Vue Stepper</h1>
    <Stepper 
      :steps="steps" 
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Stepper from './components/Stepper.vue'
import Step1 from './components/steps/Step1.vue'
import Step2 from './components/steps/Step2.vue'


const steps = ref([
  { title: 'Personal Info', component: Step1 },
  { title: 'Address', component: Step2 }
])

</script>