<template>
  <div id="app">
    <header class="header">
      <div class="logo">
        <h1>FastAPI Forge</h1>
        <a class="github-icon" href="https://github.com/mslaursen/fastapi-forge" target="_blank">
          <svg
            width="20"
            height="20"
            viewBox="0 0 98 96"
            xmlns="http://www.w3.org/2000/svg"
            class="fill-current"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z"
              fill="currentColor"
            ></path>
          </svg>
        </a>
      </div>
    </header>
    <main class="main">
      <div class="content">
        <Stepper :steps="steps" @completed="console.log('Stepper completed')" />
      </div>
    </main>
  </div>
</template>

<script setup>
import Stepper from './components/Stepper.vue'
import Step1 from './components/steps/Step1.vue'
import Step2 from './components/steps/Step2.vue'
import Step3 from './components/steps/Step3.vue'

const steps = [Step1, Step2, Step3]
</script>



<style>
html,
body {
  height: 100%;
  margin: 0;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f4f4f0;
  font-family: sans-serif;
}

.header {
  height: 60px;
  position: sticky;
  flex-shrink: 0;
  background-color: #ffffff;
  border-bottom: 4px solid black;
  top: 0;
  display: flex;
  align-items: center;
}

.content {
  flex-grow: 1;
  padding: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 1rem;
}

.github-icon {
  width: 20px;
  height: 20px;
  border: 2px solid black;
  border-radius: 15%;
  padding: 0.25rem;
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 1);
  transition: transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out;
}

.github-icon:hover {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px rgba(0, 0, 0, 1);
  cursor: pointer;
}

.github-icon:visited,
.github-icon:active,
.github-icon:focus {
  color: black;
}
</style>
