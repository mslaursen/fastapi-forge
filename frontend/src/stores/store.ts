import { defineStore } from 'pinia';
import { ref } from 'vue'


export const useProjectStore = defineStore("projectSpec", () => {
    const stepOneComplete = ref(false);
    const stepTwoComplete = ref(false);

    const projectSpec = ref({ "project_name": "", "database": "" })
    const isProjectNameConfirmed = ref(false)

    const setProjectName = (projectName: string): void => {
        projectSpec.value.project_name = projectName
    };
    const getProjectName = (): string => {
        return projectSpec.value.project_name

    };

    const setDatabase = (database: string): void => {
        projectSpec.value.database = database
    };
    const getDatabase = (): string => {
        return projectSpec.value.database
    };

    return {
        projectSpec,
        isProjectNameConfirmed,
        setProjectName,
        getProjectName,
        setDatabase,
        getDatabase
    }
});