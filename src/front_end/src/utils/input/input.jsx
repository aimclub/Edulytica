import "./input.scss"
export const Input = ({ type, placeholder, name, onChange, value }) => {
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
