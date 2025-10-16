import "./input.scss"
export const Input = ({
  type,
  placeholder,
  name,
  onChange,
  style,
  value,
  multiline = false,
}) => {
  if (multiline) {
    return (
      <textarea
        placeholder={placeholder}
        name={name}
        onChange={onChange}
        className="input"
        style={style}
      />
    )
  }
  return (
    <input
      type={type}
      placeholder={placeholder}
      name={name}
      onChange={onChange}
      value={value}
      className="input"
    />
  )
}
