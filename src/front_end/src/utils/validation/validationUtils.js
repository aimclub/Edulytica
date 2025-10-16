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

export const validateTicketName = (name) => {
  const trimmed = name.trim()
  if (!trimmed) return "* Обязательное поле"
  if (trimmed.length < 1) return "* Название не может быть пустым"
  if (trimmed.length > 60)
    return "* Название слишком длинное (максимум 60 символов)"
  return null
}

export const validateFeedbackName = (name) => {
  const trimmed = name.trim()
  if (!trimmed) return "* Обязательное поле"
  if (trimmed.length < 2) return "* Имя слишком короткое"
  if (trimmed.length > 100)
    return "* Имя слишком длинное (максимум 100 символов)"
  return null
}

export const validateFeedbackEmail = (email) => {
  const trimmed = email.trim()
  if (!trimmed) return "* Обязательное поле"
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) return "* Некорректный email"
  if (trimmed.length > 100)
    return "* Email слишком длинный (максимум 100 символов)"
  return null
}

export const validateFeedbackMessage = (message) => {
  const trimmed = message.trim()
  if (!trimmed) return "* Обязательное поле"
  if (trimmed.length < 10)
    return "* Сообщение слишком короткое (минимум 10 символов)"
  if (trimmed.length > 3000)
    return "* Сообщение слишком длинное (максимум 3000 символов)"
  return null
}

//Валидация ошибок от сервера
const ERROR_TYPES = {
  EMAIL_EXISTS: "User with such email already exists",
  LOGIN_EXISTS: "User with such login already exists",
  PASSWORDS_NOT_MATCH: "Passwords are not equal",
  INVALID_CREDENTIALS: "Credentials are incorrect",
  INVALID_CODE: "Wrong code",
  OLD_PASSWORD_INCORRECT: "Old password incorrect",
  NEW_PASSWORDS_NOT_MATCH: "New passwords not equal",
  TICKET_NOT_FOUND: "Ticket not found",
  NOT_TICKET_CREATOR: "You're not ticket creator",
  TICKET_NAME_TOO_LONG: "Ticket name too long, maximum: 60 characters",
  FEEDBACK_NAME_TOO_LONG: "The name is too long, maximum 100 characters",
  FEEDBACK_EMAIL_TOO_LONG: "The email is too long, maximum 100 characters",
  FEEDBACK_TEXT_TOO_LONG: "The text is too long, maximum 3000 characters",
  TELEGRAM_API_UNAVAILABLE: "Telegram API is unavailable",
  TELEGRAM_API_ERROR: "Telegram API error",
  TELEGRAM_RETURNED_ERROR: "Telegram returned an error",
}

export const validateBackend = (err) => {
  if (err === ERROR_TYPES.EMAIL_EXISTS) {
    return {
      email: "* Пользователь с такой почтой уже существует",
      login: null,
      password: null,
      repeatPassword: null,
    }
  }
  if (err === ERROR_TYPES.LOGIN_EXISTS) {
    return {
      email: null,
      login: "* Пользователь с таким логином уже существует",
      password: null,
      repeatPassword: null,
    }
  }
  if (err === ERROR_TYPES.PASSWORDS_NOT_MATCH) {
    return {
      email: null,
      login: null,
      password: "* Пароли не совпадают",
      repeatPassword: null,
    }
  }
  if (err === ERROR_TYPES.INVALID_CREDENTIALS) {
    return {
      name: "* Неверный логин или пароль",
      password: null,
    }
  }
  if (err === ERROR_TYPES.INVALID_CODE) {
    return {
      name: "* Неверный пароль",
    }
  }
  if (err === ERROR_TYPES.OLD_PASSWORD_INCORRECT) {
    return {
      oldPassword: "* Неверный старый пароль",
    }
  }
  if (err === ERROR_TYPES.NEW_PASSWORDS_NOT_MATCH) {
    return {
      newPassword1: "* Новые пароли не совпадают",
    }
  }
  if (err === ERROR_TYPES.TICKET_NOT_FOUND) {
    return {
      name: "* Тикет не найден",
    }
  }
  if (err === ERROR_TYPES.NOT_TICKET_CREATOR) {
    return {
      name: "* Вы не являетесь создателем этого тикета",
    }
  }
  if (err === ERROR_TYPES.TICKET_NAME_TOO_LONG) {
    return {
      name: "* Название тикета слишком длинное (максимум 60 символов)",
    }
  }
  if (err === ERROR_TYPES.FEEDBACK_NAME_TOO_LONG) {
    return {
      name: "* Имя слишком длинное (максимум 100 символов)",
    }
  }
  if (err === ERROR_TYPES.FEEDBACK_EMAIL_TOO_LONG) {
    return {
      email: "* Email слишком длинный (максимум 100 символов)",
    }
  }
  if (err === ERROR_TYPES.FEEDBACK_TEXT_TOO_LONG) {
    return {
      message: "* Сообщение слишком длинное (максимум 3000 символов)",
    }
  }
  if (err && err.includes("Telegram API is unavailable")) {
    return {
      general: "* Сервис временно недоступен. Попробуйте позже.",
    }
  }
  if (err && err.includes("Telegram API error")) {
    return {
      general: "* Ошибка сервиса. Попробуйте позже.",
    }
  }
  if (err && err.includes("Telegram returned an error")) {
    return {
      general: "* Ошибка отправки сообщения. Попробуйте позже.",
    }
  }
  return {
    general: "* Произошла неизвестная ошибка",
  }
}
