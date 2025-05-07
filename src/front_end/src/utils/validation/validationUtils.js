export const validateEmail = (email) => {
  const trimmed = email.trim()
  if (!trimmed) return "* Обязательное поле"
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) return "* Некорректный email"
  return null
}

export const validateLogin = (login) => {
  const trimmed = login.trim()
  if (!trimmed) return "* Обязательное поле"
  if (trimmed.length < 3) return "* Логин слишком короткий"
  return null
}

export const validatePassword = (password) => {
  if (!password) return "* Обязательное поле"
  if (password.length < 8) return "* Минимум 8 символов"
  if (!/\d/.test(password))
    return "* Пароль должен содержать хотя бы одну цифру"
  if (!/[a-zA-Zа-яА-Я]/.test(password))
    return "* Пароль должен содержать хотя бы одну букву"
  return null
}

export const validateRepeatPassword = (password, repeatPassword) => {
  if (!repeatPassword) return "* Обязательное поле"
  if (password && password !== repeatPassword) return "* Пароли не совпадают"
  return null
}

export const validateAuthorizationName = (name) => {
  if (!name.trim()) return "* Введите логин"
  return null
}

export const validateAuthorizationPassword = (password) => {
  if (!password.trim()) return "* Введите пароль"
  return null
}

//Валидация ошибок от сервера
const ERROR_TYPES = {
  EMAIL_EXISTS: "User with such email already exists",
  LOGIN_EXISTS: "User with such login already exists",
  PASSWORDS_NOT_MATCH: "Passwords are not equal",
  INVALID_CREDENTIALS: "Credentials are incorrect",
  INVALID_CODE: "Wrong code",
}

export const validateBackend = (err) => {
  switch (err) {
    case ERROR_TYPES.EMAIL_EXISTS:
      return {
        email: "* Пользователь с такой почтой уже существует",
        login: null,
        password: null,
        repeatPassword: null,
      }

    case ERROR_TYPES.LOGIN_EXISTS:
      return {
        email: null,
        login: "* Пользователь с таким логином уже существует",
        password: null,
        repeatPassword: null,
      }

    case ERROR_TYPES.PASSWORDS_NOT_MATCH:
      return {
        email: null,
        login: null,
        password: "* Пароли не совпадают",
        repeatPassword: null,
      }

    case ERROR_TYPES.INVALID_CREDENTIALS:
      return {
        name: "* Неверный логин или пароль",
        password: null,
      }

    case ERROR_TYPES.INVALID_CODE:
      return {
        name: "* Неверный пароль",
      }

    default:
      return {
        general: "* Произошла неизвестная ошибка",
      }
  }
}
