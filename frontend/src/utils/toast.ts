import { useToast } from "vue-toastification"
const toast = useToast()

export const showSuccessToast = (msg: string) => {
  toast.success(msg, { toastClassName: "container-class" })
}

export const showDangerToast = (msg: string) => {
  toast.error(msg, { toastClassName: "container-class" })
}

export const showWarningToast = (msg: string) => {
  toast.warning(msg, { toastClassName: "container-class" })
}
