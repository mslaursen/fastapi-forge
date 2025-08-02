export interface Position2D {
  x: number
  y: number
}

export type FieldType = "String" | "UUID" | "DateTime" | "Number" | "Boolean" | "String"

export interface RelationalField {
  name: string
  type: FieldType
  isPrimaryKey?: boolean
}

export type OnDeleteType = "CASCADE" | "SET NULL"

export interface RelationalRelationField {
  fieldName: string
  targetModel: string
  backPopulates?: string
  onDelete: OnDeleteType
  isNullable: boolean
  isUnique: boolean
  isIndex: boolean
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
}

export interface EnumValue {
  name: string
  value: string
}

export interface Enum {
  name: string
  values: Array<EnumValue>
}

export type NodesArray = Array<NodeT>
export type EdgesArray = Array<EdgeT>
export type EnumsArray = Array<Enum>
