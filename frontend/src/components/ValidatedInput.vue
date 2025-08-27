<template>
  <div class="validated-input">
    <label v-if="label" class="field-label">{{ label }}</label>

    <input
      v-bind="$attrs"
      :value="modelValue"
      @input="onInput"
      :class="{ invalid: error }"
      class="field-input"
    />

    <p v-if="error" class="error-msg">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"

interface Props {
  modelValue: string
  label?: string
  validate?: ((value: string) => boolean) | ((value: string) => string | null)
  errorMessage?: string 
}

const props = defineProps<Props>()
const emit = defineEmits(["update:modelValue"])

const error = ref<string | null>(null)

const runValidation = (value: string) => {
  if (!props.validate) {
    error.value = null
    return
  }

  const result = props.validate(value)

  if (typeof result === "boolean") {
    error.value = result ? null : (props.errorMessage ?? "Invalid value")
  } else {
    error.value = result
  }
}

const onInput = (e: Event) => {
  const value = (e.target as HTMLInputElement).value
  emit("update:modelValue", value)
  runValidation(value)
}

watch(
  () => props.modelValue,
  (newVal) => runValidation(newVal),
  { immediate: true },
)
</script>

<style scoped>
.field-label {
  font-weight: bold;
  margin-bottom: 5px;
  display: block;
}

.field-input {
  border: 2px solid black;
  border-radius: 6px;
  padding: 0.6rem;
  background-color: white;
  width: 100%;
}

.field-input.invalid {
  border-color: red;
}

.error-msg {
  color: red;
  font-size: 0.85rem;
  margin-top: 2px;
}

.validated-input {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
</style>
