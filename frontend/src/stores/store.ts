import { defineStore } from "pinia"
import { ref, shallowRef } from "vue"
import type { Ref } from "vue"
import type { NodesArray, EdgesArray,EnumsArray, NodeT, EdgeT, Field, RelationalField, RelationalRelationField, EnumValue } from "@/types/types.ts"
import type { Edge } from "@vue-flow/core"

export const useProjectStore = defineStore("projectSpec", () => {
  const projectSpec = ref({ project_name: "", database: "" })
  const isProjectNameConfirmed = ref(false)

  const enums: Ref<EnumsArray> = ref([])

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
      position: { x: 250, y: 250 },
    },
    {
      id: "Test",
      data: {
        fields: [],
        relations: [],
      },
      type: "custom",
      position: { x: 20, y: 270 },
    },
  ])

  const edges: Ref<EdgesArray> = ref([
    {
      id: "(User)-(Post)-(post_id)",
      source: "User",
      target: "Post",
    },
  ])

  const findNodeById = (id: string): NodeT | undefined => {
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
    nodes.value = nodes.value.filter(
      (node) => node.id !== id
    )
    edges.value = edges.value.filter(
      (edge) => edge.source !== id && edge.target !== id
    )
    nodes.value.forEach((node) => {
      if (node.data.relations) {
        node.data.relations = node.data.relations?.filter(
          (relation) => relation.targetModel !== id
        )
      }
    })
  }

  const renameNode = (source: string, newName: string) => {
    const node = findNodeById(source)
    if (!node) throw new Error(`Model does not exist: ${source}`)
    const existingNode = findNodeById(newName)
    if (existingNode) throw new Error(`Duplicate name: ${newName}`)
    node.id = newName
    edges.value.forEach((edge) => {
      if (edge.source === source) edge.source = newName
      if (edge.target === source) edge.target = newName
      edge.id = edge.id.replace(`(${source})`, `(${newName})`)
    })

    nodes.value.forEach((n) => {
      n.data.relations.forEach((rel) => {
        if (rel.targetModel === source) {
          rel.targetModel = newName
        }
      })
    })
  }

  const nameExistsInModel = (node: NodeT, name: string): boolean => {
    const existingFieldname = node.data.fields.find(
      (field) => field.name === name
    )
    const existingRelationFieldName = node.data.relations.find(
      (relation) => relation.fieldName === name
    )
    return !!existingFieldname || !!existingRelationFieldName;
  }

  const addField = (
    source: string,
    fieldData: RelationalField,
  ) => {
    const node = findNodeById(source)
    if (!node) throw new Error(`Model does not exist: ${source}`)
    if (nameExistsInModel(node, fieldData.name)) throw new Error(
      `Field name already exists for model: ${source}`
    );
    node.data.fields.push(fieldData)
  }

  const updateField = (source: string, originalFieldName: string, fieldData: Field) => {
    const node = findNodeById(source)
    if (!node) throw new Error(`Model does not exist: ${source}`)
    const fieldIndex = node.data.fields.findIndex((f) => f.name === originalFieldName)
    if (fieldIndex === -1) throw new Error(`Field does not exist: ${originalFieldName}`)
    node.data.fields[fieldIndex] = fieldData
  }

  const deleteField = (
    source: string,
    fieldName: string,
  ) => {
    const node = findNodeById(source)
    if (!node) return
    node.data.fields = node.data.fields.filter(
      (field) => field.name !== fieldName
    )
  }

  const addRelation = (
    source: string,
    target: string,
    relationData: RelationalRelationField,
  ): void => {
    const node = findNodeById(source)
    if (!node) return
    createEdge(source, target, relationData.fieldName)
    node.data.relations.push(relationData)
  }

  const deleteRelation = (
    source: string,
    target: string,
    fieldName: string,
  ) => {
    const node = findNodeById(source)
    if (!node) return
    node.data.relations = node.data.relations.filter(
      (relation) => relation.fieldName !== fieldName
    )
    deleteEdge(source, target, fieldName)
  }

  const updateRelation = (
    source: string,
    originalTarget: string,
    originalFieldName: string,
    relationData: RelationalRelationField,
  ): void => {
    const node = findNodeById(source)
    if (!node || !node.data.relations) return
    const index = node.data.relations.findIndex(
      (rel) => rel.fieldName === originalFieldName
    )
    node.data.relations[index] = relationData
    if (originalTarget === relationData.targetModel) return;

    const edgeId =  `(${source})-(${originalTarget})-(${originalFieldName})`
    const edge = getEdgeById(edgeId)
    if (!edge) return;

    const newEdgeId = `(${source})-(${relationData.targetModel})-(${relationData.fieldName})`
    edge.id = newEdgeId
    edge.source = source
    edge.target = relationData.targetModel
  }

  const getEdgeById = (
    id: string
  ): EdgeT | undefined => {
    return edges.value.find((edge) => edge.id === id)
  }

  const createEdge = (
    source: string, 
    target: string, 
    fieldName: string
  ): void => {
    if (source === target) return
    edges.value.push({
      id: `(${source})-(${target})-(${fieldName})`,
      source,
      target,
    })
  }

  const deleteEdge = (
    source: string, 
    target: string,
    fieldName: string
  ) => {
    edges.value = edges.value.filter(
      (edge) => edge.id !== `(${source})-(${target})-(${fieldName})`
    )
  }

  const addEnum = (name: string) => {}
  const updateEnumName = (oldName: string, newName: string) => {}
  const deleteEnum = (name: string) => {}

  const addEnumValue = (enumName: string, enumValue: EnumValue) => {}
  const updateEnumValue = (enumName: string, enumValueName: string, newEnumValue: EnumValue) => {}
  const deleteEnumValue = (enumName: string, enumValueName: string) => {}

  

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
    nodes,
    edges,
    createNode,
    createEdge,
    deleteNode,
    renameNode,
    addField,
    deleteField,
    updateField,
    addRelation,
    deleteRelation,
    updateRelation,
    projectSpec,
    isProjectNameConfirmed,
    setProjectName,
    getProjectName,
    setDatabase,
    getDatabase,
    findNodeById,
  }
})
