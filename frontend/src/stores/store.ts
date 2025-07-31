import { defineStore } from "pinia"
import { ref, shallowRef } from "vue"
import type { Ref } from "vue"
import type { NodesArray, EdgesArray, Node, RelationalField, RelationalRelationField } from "@/types/types.ts"

export const useProjectStore = defineStore("projectSpec", () => {
  const modal = ref(null)
  const modalComponent = shallowRef(null)
  const modalComponentProps = ref({})

  const projectSpec = ref({ project_name: "", database: "" })
  const isProjectNameConfirmed = ref(false)

  const nodes: Ref<NodesArray> = ref([
    {
      id: "User",
      data: {
        fields: [
          { name: "id", type: "UUID", isPrimaryKey: true },
          { name: "name", type: "String" },
          { name: "email", type: "String" },
          { name: "created_at", type: "DateTime" },
          { name: "updated_at", type: "DateTime" },
        ],
        relations: [
          {
            fieldName: "post_id",
            targetModel: "Post",
            onDelete: "CASCADE",
            isNullable: false,
            isUnique: false,
            isIndex: false,
          },
        ],
      },
      type: "custom",
      position: { x: 50, y: 50 },
    },
    {
      id: "Post",
      data: {
        fields: [
          { name: "id", type: "UUID", isPrimaryKey: true },
          { name: "created_at", type: "DateTime" },
          { name: "updated_at", type: "DateTime" },
        ],
        relations: [],
      },
      type: "custom",
      position: { x: 150, y: 150 },
    },
  ])

  const edges: Ref<EdgesArray> = ref([
    {
      id: "User>Post",
      source: "User",
      target: "Post",
    },
  ])

  const findNodeById = (id: string): Node | undefined => {
    return nodes.value.find((node) => node.id === id)
  }

  const createNode = (id: string): void => {
    if (findNodeById(id)) return
    nodes.value.push({ 
      id, 
      data: { fields:[], relations:[] },
      type: "custom", 
      position: { x: 100, y: 100 } })
  }

  const deleteNode = (id: string): void => {
    const node = findNodeById(id)
    if (!node) return
    nodes.value = nodes.value.filter((node) => node.id !== id)
    edges.value = edges.value.filter((edge) => edge.source !== id && edge.target !== id)
  }

  const addField = (
    source: string,
    fieldData: RelationalField,
  ) => {
    const node = findNodeById(source)
    if (!node) return
    node.data?.fields.push(fieldData)
  }

  const addRelation = (
    source: string,
    target: string,
    relationData: RelationalRelationField,
  ): void => {
    const node = findNodeById(source)
    if (!node) return
    createEdge(source, target)
    node.data?.relations.push(relationData)
  }

  const updateRelation = (
    source: string,
    fieldName: string,
    relationData: RelationalRelationField,
  ): void => {
    const node = findNodeById(source)
    if (!node || !node.data?.relations) return
    const index = node.data.relations.findIndex((rel) => rel.fieldName === fieldName)
    node.data.relations[index] = relationData
    console.log(index)
  }

  const createEdge = (source: string, target: string): void => {
    if (source === target) return
    edges.value.push({
      id: `${source}-${target}`,
      source,
      target,
    })
  }

  const setProjectName = (projectName: string): void => {
    projectSpec.value.project_name = projectName
  }
  const getProjectName = (): string => {
    return projectSpec.value.project_name
  }

  const setDatabase = (database: string): void => {
    projectSpec.value.database = database
  }
  const getDatabase = (): string => {
    return projectSpec.value.database
  }

  return {
    modal,
    modalComponent,
    modalComponentProps,
    nodes,
    edges,
    createNode,
    createEdge,
    deleteNode,
    addField,
    addRelation,
    updateRelation,
    projectSpec,
    isProjectNameConfirmed,
    setProjectName,
    getProjectName,
    setDatabase,
    getDatabase,
  }
})
