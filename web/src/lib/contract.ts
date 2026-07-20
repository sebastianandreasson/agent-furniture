export type JsonRecord = Record<string, unknown>
export type FieldRule<T = unknown> = (value: unknown) => value is T
type FieldRules = Record<string, FieldRule>
type FieldsOf<Rules extends FieldRules> = {
  [Name in keyof Rules]: Rules[Name] extends FieldRule<infer Value>
    ? Value
    : never
}

export const field = {
  array: (value: unknown): value is unknown[] => Array.isArray(value),
  boolean: (value: unknown): value is boolean => typeof value === 'boolean',
  finite: (value: unknown): value is number =>
    typeof value === 'number' && Number.isFinite(value),
  integer: (value: unknown): value is number =>
    typeof value === 'number' && Number.isInteger(value),
  nonEmptyString: (value: unknown): value is string =>
    typeof value === 'string' && value.trim().length > 0,
  nonnegativeInteger: (value: unknown): value is number =>
    typeof value === 'number' && Number.isInteger(value) && value >= 0,
  positive: (value: unknown): value is number =>
    typeof value === 'number' && Number.isFinite(value) && value > 0,
  positiveInteger: (value: unknown): value is number =>
    typeof value === 'number' && Number.isInteger(value) && value > 0,
  string: (value: unknown): value is string => typeof value === 'string',
  stringArray: (value: unknown): value is string[] =>
    Array.isArray(value) && value.every((item) => typeof item === 'string'),
} satisfies FieldRules

export function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null
}

export function expectFields<Rules extends FieldRules>(
  value: unknown,
  rules: Rules,
  message: string,
): JsonRecord & FieldsOf<Rules> {
  if (
    !isRecord(value) ||
    Object.entries(rules).some(([name, rule]) => !rule(value[name]))
  ) {
    throw new Error(message)
  }
  return value as JsonRecord & FieldsOf<Rules>
}
