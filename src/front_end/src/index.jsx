import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import "./assets/css/global.scss"
import { Provider } from "react-redux"
import store from "./store/store.js"
const root = ReactDOM.createRoot(document.getElementById("root"))
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
)
