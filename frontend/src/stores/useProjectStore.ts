import { defineStore } from "pinia"
import { ref } from "vue"
import type { Ref } from "vue"
import type {
  NodesArray,
  EdgesArray,
  EnumsArray,
  NodeT,
  EdgeT,
  RelationalField,
  RelationalRelationField,
  EnumValue,
  EnumT,
} from "@/types/types.ts"

export const useProjectStore = defineStore("projectSpec", () => {
  const projectSpec = ref({ project_name: "asd", database: "", models: [], custom_enums: [] })
  const isProjectNameConfirmed = ref(false)

  const enums: Ref<EnumsArray> = ref([
    {
      name: "UserRole",
      values: [
        { name: "ADMIN", value: "ADMIN" },
        { name: "USER", value: "auto()" },
      ],
    },
  ])

  const nodes: Ref<NodesArray> = ref([
    {
      id: "user",
      data: {
        fields: [
          { name: "id", type: "UUID", isPrimaryKey: true, defaultValue: "uuid.uuid4" },
          { name: "name", type: "String" },
          { name: "email", type: "String" },
          { name: "role", type: "Enum", typeEnum: "UserRole", defaultValue: "ADMIN" },
          { name: "created_at", type: "DateTime" },
          { name: "updated_at", type: "DateTime" },
        ],
        relations: [
          {
            fieldName: "post_id",
            targetModel: "post",
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
      id: "post",
      data: {
        fields: [
          { name: "id", type: "UUID", isPrimaryKey: true, defaultValue: "uuid.uuid4" },
          { name: "created_at", type: "DateTime" },
          { name: "updated_at", type: "DateTime" },
        ],
        relations: [],
      },
      type: "custom",
      position: { x: 150, y: 355 },
    },
  ])

  const edges: Ref<EdgesArray> = ref([
    {
      id: "(user)-(post)-(post_id)",
      source: "user",
      target: "post",
      type: "smoothstep",
    },
  ])

  const convertToPayload = () => {
    const models = nodes.value.map((node) => {
      const modelName = node.id

      const fields = node.data.fields.map((field) => {
        return {
          name: field.name,
          type: field.type,
          type_enum: field.typeEnum ?? null,
          primary_key: field.isPrimaryKey ?? false,
          nullable: field.isNullable ?? false,
          unique: field.isUnique ?? false,
          index: field.isIndex ?? false,
          default_value: field.defaultValue ?? null,
          extra_kwargs: null,
          metadata: {
            is_created_at_timestamp: field.name === "created_at",
            is_updated_at_timestamp: field.name === "updated_at",
            is_foreign_key: false,
          },
        }
      })

      const relationships = node.data.relations.map((relation) => {
        return {
          field_name: relation.fieldName,
          target_model: relation.targetModel,
          back_populates: null,
          on_delete: relation.onDelete ?? "CASCADE",
          nullable: relation.isNullable ?? false,
          unique: relation.isUnique ?? false,
          index: relation.isIndex ?? false,
        }
      })

      return {
        name: modelName,
        fields,
        relationships,
        metadata: {
          create_endpoints: true,
          create_tests: true,
          create_daos: true,
          create_dtos: true,
          is_auth_model: false,
        },
      }
    })

    const custom_enums = enums.value.map((enm) => {
      return {
        name: enm.name,
        values: enm.values.map((val) => ({
          name: val.name,
          value: val.value,
        })),
      }
    })

    return {
      project_name: projectSpec.value.project_name,
      use_postgres: true,
      use_alembic: true,
      models,
      custom_enums,
    }
  }

  const callGenerateEndpoint = async () => {
    const payload = convertToPayload()

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Error ${response.status}: ${errorText}`)
      }

      const result = await response.json()
      console.log("Generation successful:", result)
      return result
    } catch (error) {
      console.error("Generation failed:", error)
      throw error
    }
  }

  const findNodeById = (id: string): NodeT | undefined => {
    return nodes.value.find((node) => node.id === id)
  }

  const createNode = (id: string): void => {
    if (findNodeById(id)) return
    nodes.value.push({
      id,
      data: { fields: [], relations: [] },
      type: "custom",
      position: { x: 100, y: 100 },
    })
  }

  const deleteNode = (id: string): void => {
    const node = findNodeById(id)
    if (!node) return
    nodes.value = nodes.value.filter((node) => node.id !== id)
    edges.value = edges.value.filter((edge) => edge.source !== id && edge.target !== id)
    nodes.value.forEach((node) => {
      if (node.data.relations) {
        node.data.relations = node.data.relations?.filter((relation) => relation.targetModel !== id)
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
    const existingFieldname = node.data.fields.find((field) => field.name === name)
    const existingRelationFieldName = node.data.relations.find(
      (relation) => relation.fieldName === name,
    )
    return !!existingFieldname || !!existingRelationFieldName
  }

  const addField = (source: string, fieldData: RelationalField) => {
    const node = findNodeById(source)
    if (!node) throw new Error(`Model does not exist: ${source}`)
    if (nameExistsInModel(node, fieldData.name))
      throw new Error(`Field name already exists for model: ${source}`)
    node.data.fields.push(fieldData)
  }

  const updateField = (source: string, originalFieldName: string, fieldData: RelationalField) => {
    const node = findNodeById(source)
    if (!node) throw new Error(`Model does not exist: ${source}`)
    const fieldIndex = node.data.fields.findIndex((f) => f.name === originalFieldName)
    if (fieldIndex === -1) throw new Error(`Field does not exist: ${originalFieldName}`)
    node.data.fields[fieldIndex] = fieldData
    console.log(fieldData)
  }

  const deleteField = (source: string, fieldName: string) => {
    const node = findNodeById(source)
    if (!node) throw new Error(`Model does not exist: ${source}`)
    node.data.fields = node.data.fields.filter((field) => field.name !== fieldName)
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

  const deleteRelation = (source: string, target: string, fieldName: string) => {
    const node = findNodeById(source)
    if (!node) return
    node.data.relations = node.data.relations.filter((relation) => relation.fieldName !== fieldName)
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
    const index = node.data.relations.findIndex((rel) => rel.fieldName === originalFieldName)
    node.data.relations[index] = relationData

    const edgeId = formatEdgeId(source, originalTarget, originalFieldName)
    const edge = getEdgeById(edgeId)
    if (!edge) return

    const newEdgeId = formatEdgeId(source, relationData.targetModel, relationData.fieldName)
    edge.id = newEdgeId
    edge.source = source
    edge.target = relationData.targetModel
  }

  const getEdgeById = (id: string): EdgeT | undefined => {
    return edges.value.find((edge) => edge.id === id)
  }

  const formatEdgeId = (source: string, target: string, fieldName: string): string => {
    return `(${source})-(${target})-(${fieldName})`
  }

  const createEdge = (source: string, target: string, fieldName: string): void => {
    if (source === target) return
    edges.value.push({
      id: formatEdgeId(source, target, fieldName),
      source,
      target,
      type: "smoothstep",
    })
  }

  const deleteEdge = (source: string, target: string, fieldName: string) => {
    edges.value = edges.value.filter((edge) => edge.id !== formatEdgeId(source, target, fieldName))
  }

  const findEnumByName = (name: string): EnumT => {
    const en = enums.value.find((e) => e.name === name)
    if (!en) throw Error(`Enum not found: ${name}`)
    return en
  }

  const findEnumValue = (enumName: string, enumValueName: string): EnumValue => {
    const en = findEnumByName(enumName)
    const ev = en.values.find((v) => v.name === enumValueName)
    if (!ev) throw Error(`EnumValue not found: ${enumValueName}`)
    return ev
  }

  const addEnum = (name: string): EnumT => {
    const newEnum = { name: name, values: [] }
    enums.value.push(newEnum)
    return newEnum
  }
  const updateEnumName = (oldName: string, newName: string) => {
    const en = findEnumByName(oldName)
    en.name = newName
    nodes.value.forEach((n) => {
      n.data.fields.forEach((f) => {
        if (f.type === "Enum" && f.typeEnum === oldName) {
          f.typeEnum = newName
        }
      })
    })
  }
  const deleteEnum = (name: string) => {
    enums.value = enums.value.filter((e) => e.name !== name)
    nodes.value.forEach((n) => {
      n.data.fields = n.data.fields.filter((f) => f.typeEnum !== name)
    })
  }

  const addEnumValue = (enumName: string, enumValue: EnumValue) => {
    const en = findEnumByName(enumName)
    en.values.push(enumValue)
  }
  const updateEnumValue = (enumName: string, enumValueName: string, newEnumValue: EnumValue) => {
    const ev = findEnumValue(enumName, enumValueName)
    ev.name = newEnumValue.name
    ev.value = newEnumValue.value

    console.log(enumName)
    console.log(newEnumValue)

    nodes.value.forEach((n) => {
      n.data.fields.forEach((f) => {
        if (f.type === "Enum" && f.typeEnum === enumName) {
          f.defaultValue = newEnumValue.name
        }
      })
    })
  }
  const deleteEnumValue = (enumName: string, enumValueName: string) => {
    const en = findEnumByName(enumName)
    en.values = en.values.filter((e) => e.name !== enumValueName)
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
    nodes,
    edges,
    enums,
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
    findEnumByName,
    addEnum,
    updateEnumName,
    deleteEnum,
    addEnumValue,
    updateEnumValue,
    deleteEnumValue,
    convertNodesToModel: convertToPayload,
    callGenerateEndpoint,
  }
})
