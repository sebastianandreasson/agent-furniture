export function NumericField({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (value: number) => void
}) {
  return (
    <label className="numeric-field">
      <span>{label}</span>
      <input
        type="number"
        value={value}
        step={10}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  )
}

export function ArtifactLink({
  href,
  label,
}: {
  href?: string
  label: string
}) {
  if (!href) return null
  return (
    <a className="artifact-link" href={href} target="_blank" rel="noreferrer">
      <span>{label}</span>
      <span aria-hidden="true">↗</span>
    </a>
  )
}
