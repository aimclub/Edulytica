export const validateEmail = (email) => {
  const trimmed = email.trim()
  if (!trimmed) return "* Обязательное поле"
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) return "* Некорректный email"
  return null
}

export const validateLogin = (login, users) => {
  const trimmed = login.trim()
  if (!trimmed) return "* Обязательное поле"
  if (trimmed.length < 3) return "* Логин слишком короткий"
  if (users.some((user) => user.login === trimmed))
    return "* Этот логин уже занят"
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

export const validateUserCredentials = (name, password, users) => {
  const user = users.find(
    (user) =>
      (user.login === name || user.email === name) && user.password === password
  )
  if (!user && name.trim() && password.trim())
    return "* Неверный логин или пароль"
  return null
}
