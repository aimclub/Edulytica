import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import "./assets/css/global.scss"
import { Provider } from "react-redux"
import store from "./store/store"
import $api, { API_URL } from "./api/axios.api"
import axios from "axios"
import { loginUser } from "./store/authSlice"
import { forceLogout } from "./utils/authUtils"

// Lightweight 401 refresh logic remains, errors транслируем в api:error из axios.api.js
$api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      !originalRequest?.url?.includes("/auth/logout") &&
      !originalRequest?.url?.includes("/auth/get_access")
    ) {
      originalRequest._retry = true
      try {
        const resp = await axios.get(`${API_URL}/auth/get_access`, {
          withCredentials: true,
        })
        store.dispatch(loginUser({ token: resp.data.access_token }))
        originalRequest.headers.Authorization = `Bearer ${resp.data.access_token}`
        return $api.request(originalRequest)
      } catch (refreshError) {
        await forceLogout("Сессия истекла")
      }
    }
    return Promise.reject(error)
  }
)

// Упрощаем: dev-overlay скрыт ниже; общую транслирующую логику держим в axios.api.js

// Hide CRA/Webpack dev overlay to use our custom notification modal
;(function suppressDevOverlay() {
  try {
    const hide = () => {
      const selectors = [
        "#webpack-dev-server-client-overlay",
        "#react-error-overlay",
        ".webpack-dev-server-overlay",
      ]
      selectors.forEach((sel) => {
        document.querySelectorAll(sel).forEach((el) => {
          el.style.setProperty("display", "none", "important")
          el.style.setProperty("visibility", "hidden", "important")
          el.remove()
        })
      })
    }

    // Initial attempt
    if (
      document.readyState === "complete" ||
      document.readyState === "interactive"
    ) {
      hide()
    } else {
      window.addEventListener("DOMContentLoaded", hide, { once: true })
    }

    // Observe future injections
    const observer = new MutationObserver(hide)
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    })
  } catch (_) {}
})()

const root = ReactDOM.createRoot(document.getElementById("root"))
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
)
