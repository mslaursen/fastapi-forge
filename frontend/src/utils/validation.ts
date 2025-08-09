const patterns = {
  boundedStr: /^.{1,100}$/,
  snakeCase: /^[a-z][a-z0-9_]*$/,
  pascalCase: /^[A-Z][a-z]*$/,
  enumStr: /^[a-zA-Z][a-zA-Z0-9_]*$/,
  variableStr: /^[a-zA-Z_][a-zA-Z0-9_-]*$/,
}

export const isValidProjectName = (value: string): boolean => {
  return patterns.boundedStr.test(value) && patterns.variableStr.test(value)
}

export const isValidModelName = (value: string): boolean => {
  return patterns.boundedStr.test(value) && patterns.variableStr.test(value)
}

export const isValidEnumName = (value: string): boolean => {
  return patterns.boundedStr.test(value) && patterns.pascalCase.test(value)
}
export const isValidEnumValueName = (value: string): boolean => {
  return patterns.boundedStr.test(value) && patterns.variableStr.test(value)
}

export const isValidFieldName = (value: string): boolean => {
  return patterns.boundedStr.test(value) && patterns.snakeCase.test(value)
}

export const warningMessages = {
  projectName: "Use 1-100 characters. Start with a letter or underscore. Example: my_project1",
  modelName: "Use 1-100 characters. Start with a letter or underscore. Example: userModel_1",
  enumName: "Use PascalCase (start with uppercase). Example: UserStatus",
  enumValueName: "Use 1-100 characters. Start with a letter or underscore. Example: active_status",
  fieldName: "Use lowercase snake_case. Example: user_name",
}
