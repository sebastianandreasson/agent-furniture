export function formatModelName(value: string) {
  return value.replaceAll(/[-_]+/g, ' ')
}
