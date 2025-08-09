import "./assets/main.css"
import "vue-toastification/dist/index.css"

import { createApp } from "vue"
import { createPinia } from "pinia"
import Toast, { POSITION, type PluginOptions } from "vue-toastification"
import App from "./App.vue"

const app = createApp(App)

app.use(createPinia())

const options: PluginOptions = {
  position: POSITION.TOP_CENTER,
  shareAppContext: true,
  containerClassName: "container-class",
}

app.use(Toast, options)

app.mount("#app")
