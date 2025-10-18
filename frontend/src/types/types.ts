export interface Position2D {
  x: number
  y: number
}

export type FieldType = "String" | "UUID" | "DateTime" | "Number" | "Boolean" | "String" | "Enum"

export interface RelationalFieldMetadata {
  isCreatedAtTimestamp?: boolean
  isUpdatedAtTimestamp?: boolean
}

export interface RelationalField {
  name: string
  type: FieldType
  typeEnum?: string
  isPrimaryKey?: boolean
  isNullable?: boolean
  isUnique?: boolean
  isIndex?: boolean
  defaultValue?: string
  metadata?: RelationalFieldMetadata
  extraKwargs?: object
}

export type OnDeleteType = "CASCADE" | "SET NULL"

export interface RelationalRelationField {
  fieldName: string
  targetModel: string
  onDelete: OnDeleteType
  backPopulates?: string
  isNullable?: boolean
  isUnique?: boolean
  isIndex?: boolean
}

export interface RelationalNodeData {
  fields: Array<RelationalField>
  relations: Array<RelationalRelationField>
}

export interface NodeT {
  id: string
  data: RelationalNodeData
  type: string
  position: Position2D
}

export interface EdgeT {
  id: string
  source: string
  target: string
  type: string
}

export interface EnumValue {
  name: string
  value: string
}

export interface EnumT {
  name: string
  values: Array<EnumValue>
}

export type NodesArray = Array<NodeT>
export type EdgesArray = Array<EdgeT>
export type EnumsArray = Array<EnumT>
