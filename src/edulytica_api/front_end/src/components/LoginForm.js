import React from "react"
import axios from "axios"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../provider/authProvider"
import '../css/main.css'
const LoginForm = (props) => {
  const { setToken } = useAuth();
  const navigate = useNavigate();

  async function btn_click() {
    const form = document.getElementById('login_form')
    const data = new FormData(form)
    return await loginUser(props.url, data)
  }
  async function loginUser(url, credentials) {
    axios.post(url, credentials, { withCredentials: true, })
      .then(response => {
        setToken(response.data.access_token)
        navigate("/", { replace: true });
      })
      .catch(error => console.error(error));
  }

  return (
    <div>
      <div className="entry-content">
        <div className="login">
          <form
            name="autorize"
            method="post"
            id="login_form"
            ectype="application/x-www-form-urlencoded"
          >
            <p><input className="loginInput" type="text" name="username" required="" placeholder="Логин" /></p>
            <p><input className="loginInput"  type="password" name="password" required="" placeholder="Пароль" /></p>
            <p className="submit"><input type="button" name="commit" value="Войти" onClick={btn_click} /></p>
          </form>
        </div>

        <div className="clearfix"></div>
      </div>
    </div>
  )
    ;
};

export default LoginForm;