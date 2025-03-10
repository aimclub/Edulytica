import ReactDOM from "react-dom/client"
import { StrictMode } from "react"
import App from "./components/App"
import "./assets/css/global.scss"
import { BrowserRouter } from "react-router-dom"

ReactDOM.createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
)
