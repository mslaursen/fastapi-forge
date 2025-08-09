export const patterns = {
  boundedStr: /^.{1,100}$/,
  snakeCase: /^[a-z][a-z0-9_]*$/,
  enumStr: /^[a-zA-Z][a-zA-Z0-9_]*$/,
  projectName: /^[a-zA-Z_][a-zA-Z0-9_-]*$/,
}

export const isValidProjectName = (value: string): boolean => {
  return patterns.boundedStr.test(value) && patterns.projectName.test(value)
}
