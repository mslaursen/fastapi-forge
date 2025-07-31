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

export interface Node {
  id: string
  data?: RelationalNodeData
  type: string
  position: Position2D
}

export interface Edge {
  id: string
  source: string
  target: string
}

export type NodesArray = Array<Node>
export type EdgesArray = Array<Edge>
