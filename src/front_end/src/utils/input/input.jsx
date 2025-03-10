import "./input.scss"
export const Input = (props) => {
  return (
    <input
      type={props.type}
      placeholder={props.placeholder}
      className="input"
    />
  )
}
