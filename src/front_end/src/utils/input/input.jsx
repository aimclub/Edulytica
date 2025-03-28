import "./input.scss"
export const Input = ({ type, placeholder, name, onChange }) => {
  return (
    <input
      type={type}
      placeholder={placeholder}
      name={name}
      onChange={onChange}
      className="input"
    />
  )
}
