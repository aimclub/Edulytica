import {
  validateEmail,
  validateLogin,
  validatePassword,
  validateRepeatPassword,
  validateAuthorizationName,
  validateAuthorizationPassword,
} from "../src/utils/validation/validationUtils"

describe("validateEmail", () => {
  test("should return null for valid email", () => {
    expect(validateEmail("test@example.com")).toBeNull()
    expect(validateEmail("user.name@domain.co.uk")).toBeNull()
    expect(validateEmail("user+tag@example.com")).toBeNull()
  })

  test("should return error message for invalid email", () => {
    expect(validateEmail("")).toBe("* Обязательное поле")
    expect(validateEmail("test@")).toBe("* Некорректный email")
    expect(validateEmail("test@example")).toBe("* Некорректный email")
    expect(validateEmail("test@.com")).toBe("* Некорректный email")
    expect(validateEmail("@example.com")).toBe("* Некорректный email")
  })
})

describe("validateLogin", () => {
  test("should return null for valid login", () => {
    expect(validateLogin("username")).toBeNull()
    expect(validateLogin("user123")).toBeNull()
    expect(validateLogin("user_name")).toBeNull()
    expect(validateLogin("user-name")).toBeNull()
  })

  test("should return error message for invalid login", () => {
    expect(validateLogin("")).toBe("* Обязательное поле")
    expect(validateLogin("ab")).toBe("* Логин слишком короткий")
  })
})

describe("validatePassword", () => {
  test("should return null for valid password", () => {
    expect(validatePassword("Password1")).toBeNull()
    expect(validatePassword("Пароль123")).toBeNull()
  })

  test("should return error message for invalid password", () => {
    expect(validatePassword("")).toBe("* Обязательное поле")
    expect(validatePassword("short")).toBe("* Минимум 8 символов")
    expect(validatePassword("longbutnodigit")).toBe(
      "* Пароль должен содержать хотя бы одну цифру"
    )
    expect(validatePassword("12345678")).toBe(
      "* Пароль должен содержать хотя бы одну букву"
    )
  })
})

describe("validateRepeatPassword", () => {
  test("should return null when passwords match", () => {
    expect(validateRepeatPassword("Password123", "Password123")).toBeNull()
  })

  test("should return error message when repeat password is empty", () => {
    expect(validateRepeatPassword("Password123", "")).toBe(
      "* Обязательное поле"
    )
  })

  test("should return error message when passwords don't match", () => {
    expect(validateRepeatPassword("Password123", "Password321")).toBe(
      "* Пароли не совпадают"
    )
  })
})

describe("validateAuthorizationName", () => {
  test("should return null for valid input", () => {
    expect(validateAuthorizationName("username")).toBeNull()
    expect(validateAuthorizationName("test@example.com")).toBeNull()
  })

  test("should return error message for empty input", () => {
    expect(validateAuthorizationName("")).toBe("* Введите логин")
    expect(validateAuthorizationName("   ")).toBe("* Введите логин")
  })
})

describe("validateAuthorizationPassword", () => {
  test("should return null for valid password", () => {
    expect(validateAuthorizationPassword("somepassword")).toBeNull()
    expect(validateAuthorizationPassword("P@ssw0rd")).toBeNull()
  })

  test("should return error message for empty password", () => {
    expect(validateAuthorizationPassword("")).toBe("* Введите пароль")
    expect(validateAuthorizationPassword("   ")).toBe("* Введите пароль")
  })
})
