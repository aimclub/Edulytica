import {
  validateEmail,
  validateLogin,
  validatePassword,
  validateRepeatPassword,
  validateAuthorizationName,
  validateAuthorizationPassword,
  validateUserCredentials,
} from "./validationUtils"

describe("validateEmail", () => {
  test("должен вернуть ошибку, если email пустой", () => {
    expect(validateEmail("")).toBe("* Обязательное поле")
  })

  test("должен вернуть ошибку, если email некорректный", () => {
    expect(validateEmail("not-an-email")).toBe("* Некорректный email")
  })

  test("валидный email не должен возвращать ошибку", () => {
    expect(validateEmail("test@example.com")).toBeNull()
  })
})

describe("validateLogin", () => {
  const users = [{ login: "fedorova_23" }]

  test("должен вернуть ошибку, если логин пустой", () => {
    expect(validateLogin("", users)).toBe("* Обязательное поле")
  })

  test("должен вернуть ошибку, если логин слишком короткий", () => {
    expect(validateLogin("ab", users)).toBe("* Логин слишком короткий")
  })

  test("должен вернуть ошибку, если логин уже занят", () => {
    expect(validateLogin("fedorova_23", users)).toBe("* Этот логин уже занят")
  })

  test("валидный логин не должен возвращать ошибку", () => {
    expect(validateLogin("newUser", users)).toBeNull()
  })
})

describe("validatePassword", () => {
  test("должен вернуть ошибку, если пароль пустой", () => {
    expect(validatePassword("")).toBe("* Обязательное поле")
  })

  test("должен вернуть ошибку, если пароль короче 8 символов", () => {
    expect(validatePassword("Abc123")).toBe("* Минимум 8 символов")
  })

  test("должен вернуть ошибку, если нет цифры", () => {
    expect(validatePassword("Password")).toBe(
      "* Пароль должен содержать хотя бы одну цифру"
    )
  })

  test("должен вернуть ошибку, если нет буквы", () => {
    expect(validatePassword("12345678")).toBe(
      "* Пароль должен содержать хотя бы одну букву"
    )
  })

  test("валидный пароль не должен возвращать ошибку", () => {
    expect(validatePassword("Pass1234")).toBeNull()
  })
})

describe("validateRepeatPassword", () => {
  test("должен вернуть ошибку, если поле повтора пустое", () => {
    expect(validateRepeatPassword("password", "")).toBe("* Обязательное поле")
  })

  test("должен вернуть ошибку, если пароли не совпадают", () => {
    expect(validateRepeatPassword("password1", "password2")).toBe(
      "* Пароли не совпадают"
    )
  })

  test("совпадающие пароли не должны возвращать ошибку", () => {
    expect(validateRepeatPassword("password", "password")).toBeNull()
  })
})

describe("validateAuthorizationName", () => {
  test("должен вернуть ошибку, если логин пустой", () => {
    expect(validateAuthorizationName("   ")).toBe("* Введите логин")
  })

  test("валидный логин не должен возвращать ошибку", () => {
    expect(validateAuthorizationName("admin")).toBeNull()
  })
})

describe("validateAuthorizationPassword", () => {
  test("должен вернуть ошибку, если пароль пустой", () => {
    expect(validateAuthorizationPassword("  ")).toBe("* Введите пароль")
  })

  test("валидный пароль не должен возвращать ошибку", () => {
    expect(validateAuthorizationPassword("secret23")).toBeNull()
  })
})

describe("validateUserCredentials", () => {
  const users = [
    { login: "admin", email: "admin@example.com", password: "12345678" },
  ]

  test("должен вернуть ошибку при неверных данных", () => {
    expect(validateUserCredentials("wrong", "wrong", users)).toBe(
      "* Неверный логин или пароль"
    )
  })

  test("валидный логин и пароль не должны возвращать ошибку", () => {
    expect(validateUserCredentials("admin", "12345678", users)).toBeNull()
  })

  test("валидный email и пароль не должны возвращать ошибку", () => {
    expect(
      validateUserCredentials("admin@example.com", "12345678", users)
    ).toBeNull()
  })
})
