import { defineStore } from 'pinia';
import { ref } from 'vue'


export const useProjectStore = defineStore("projectSpec", () => {
    const stepOneComplete = ref(false);

    const projectSpec = ref({ "project_name": "" })
    const isProjectNameConfirmed = ref(false)

    const setProjectName = (projectName: string): void => {
        projectSpec.value.project_name = projectName
    };
    const getProjectName = (): string => {
        return projectSpec.value.project_name

    }

    return { projectSpec, isProjectNameConfirmed, setProjectName, getProjectName }
});