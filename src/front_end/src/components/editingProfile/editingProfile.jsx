import { useEffect, useState } from "react"
import "./editingProfile.scss"
import $api from "../../api/axios.api"
import {
  validatePassword,
  validateBackend,
} from "../../utils/validation/validationUtils"

export const EditingProfile = ({
  setEditingProfileModal,
  infoProfile,
  setInfoProfile,
}) => {
  const [openEditingProfileModal, setOpenEditingProfileModal] = useState("info")
  const [localProfile, setLocalProfile] = useState(infoProfile)
  const [oldPassword, setOldPassword] = useState("")
  const [newPassword1, setNewPassword1] = useState("")
  const [newPassword2, setNewPassword2] = useState("")
  const [passwordErrors, setPasswordErrors] = useState({})

  /**
   * Обновляет локальное состояние при изменении infoProfile.
   */
  useEffect(() => {
    setLocalProfile(infoProfile)
  }, [infoProfile])

  /**
   * Обработчик изменения полей формы редактирования профиля.
   * Обновляет локальное состояние профиля при вводе данных.
   *
   * @param {Event} e - Событие изменения поля ввода
   * @param {string} e.target.name - Имя поля (name, surname, organization)
   * @param {string} e.target.value - Новое значение поля
   */
  const handleChangeInfo = (e) => {
    const { name, value } = e.target
    setLocalProfile((prev) => ({ ...prev, [name]: value }))
    console.log("Обновленный профиль:", localProfile)
  }

  /**
   * Обработчик отправки формы редактирования профиля.
   * Отправляет обновленные данные профиля на сервер и обновляет локальное состояние.
   */
  const handleEditingProfileModal = async () => {
    try {
      const payload = {
        name: localProfile.name,
        surname: localProfile.surname,
        organization: localProfile.organization,
      }
      await $api.patch("/account", payload)
      setOpenEditingProfileModal("info")
      setInfoProfile(localProfile)
      setEditingProfileModal(false)
    } catch (error) {
      console.error("Ошибка при обновлении профиля:", error)
    }
  }

  /**
   * Валидация формы сброса пароля.
   * Проверяет корректность введенных паролей и возвращает ошибки валидации.
   * @returns {Object} Объект с ошибками валидации или пустой объект, если ошибок нет.
   */
  const validatePasswordForm = () => {
    const newErrors = {
      oldPassword: validatePassword(oldPassword),
      newPassword1: validatePassword(newPassword1),
      newPassword2: validatePassword(newPassword2),
    }
    Object.keys(newErrors).forEach(
      (key) => newErrors[key] === null && delete newErrors[key]
    )
    setPasswordErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Обработчик сброса пароля.
   * Валидирует введенные данные и отправляет их на сервер для сброса пароля.
   * Обновляет локальное состояние и закрывает модальное окно.
   */
  const handlePasswordReset = async () => {
    if (!validatePasswordForm()) return
    try {
      await $api.post("/account/password", {
        old_password: oldPassword,
        new_password1: newPassword1,
        new_password2: newPassword2,
      })
      setOpenEditingProfileModal("info")
      setEditingProfileModal(false)
    } catch (err) {
      let backendErrors = {}
      if (err?.response?.data?.detail) {
        backendErrors = validateBackend(err.response.data.detail)
      }
      setPasswordErrors((prev) => ({ ...prev, ...backendErrors }))
    }
  }

  return (
    <div className="editingProfile">
      {openEditingProfileModal === "info" ? (
        <>
          <div className="titleEditingProfile">Профиль</div>
          <div className="containerEditingProfile">
            <div className="blockInputEditingProfile">
              <div className="titleInputEditingProfile">Имя</div>
              <input
                type="text"
                className="inputEditingProfile"
                placeholder={
                  infoProfile.name !== "..." && infoProfile.name !== ""
                    ? infoProfile.name
                    : "Введите ваше имя..."
                }
                name="name"
                value={localProfile.name}
                onChange={handleChangeInfo}
              />
            </div>
            <div className="blockInputEditingProfile">
              <div className="titleInputEditingProfile">Фамилия</div>
              <input
                type="text"
                className="inputEditingProfile"
                placeholder={
                  infoProfile.surname !== "..." && infoProfile.surname !== ""
                    ? infoProfile.surname
                    : "Введите вашу фамилию..."
                }
                name="surname"
                value={localProfile.surname}
                onChange={handleChangeInfo}
              />
            </div>
            <div className="blockInputEditingProfile">
              <div className="titleInputEditingProfile">Организация</div>
              <input
                type="text"
                className="inputEditingProfile"
                placeholder={
                  infoProfile.organization !== "..." &&
                  infoProfile.organization !== " "
                    ? infoProfile.organization
                    : "Введите вашу организацию..."
                }
                name="organization"
                value={localProfile.organization}
                onChange={handleChangeInfo}
              />
            </div>
            <div
              className="btnBottomEditingProfile"
              onClick={handleEditingProfileModal}
            >
              Изменить
            </div>
          </div>
          <div
            className="passwordResetEditingProfile"
            onClick={() => setOpenEditingProfileModal("password")}
          >
            Сбросить пароль →
          </div>
          <svg
            onClick={() => setEditingProfileModal(false)}
            className="closeButtonEditingProfile"
            width="24"
            height="24"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M8.53464 25.3327L6.66797 23.466L14.1346 15.9993L6.66797 8.53268L8.53464 6.66602L16.0013 14.1327L23.468 6.66602L25.3346 8.53268L17.868 15.9993L25.3346 23.466L23.468 25.3327L16.0013 17.866L8.53464 25.3327Z"
              fill="white"
            />
          </svg>
        </>
      ) : openEditingProfileModal === "password" ? (
        <>
          <div className="titleEditingProfile">Сброс пароля</div>
          <div className="containerEditingProfile">
            <div className="blockInputEditingProfile">
              <div className="titleInputEditingProfile">Старый пароль</div>
              <input
                type="password"
                className="inputEditingProfile"
                placeholder="Введите старый пароль..."
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
              />
              {passwordErrors.oldPassword && (
                <div className="errorTextEditingProfile">
                  {passwordErrors.oldPassword}
                </div>
              )}
            </div>
            <div className="blockInputEditingProfile">
              <div className="titleInputEditingProfile">
                Введите новый пароль
              </div>
              <input
                type="password"
                className="inputEditingProfile"
                placeholder="Введите новый пароль..."
                value={newPassword1}
                onChange={(e) => setNewPassword1(e.target.value)}
              />
              {passwordErrors.newPassword1 && (
                <div className="errorTextEditingProfile">
                  {passwordErrors.newPassword1}
                </div>
              )}
            </div>
            <div className="blockInputEditingProfile">
              <div className="titleInputEditingProfile">
                Введите повторно новый пароль
              </div>
              <input
                type="password"
                className="inputEditingProfile"
                placeholder="Введите повторно новый пароль..."
                value={newPassword2}
                onChange={(e) => setNewPassword2(e.target.value)}
              />
              {passwordErrors.newPassword2 && (
                <div className="errorTextEditingProfile">
                  {passwordErrors.newPassword2}
                </div>
              )}
            </div>
            <div
              className="btnBottomEditingProfile"
              onClick={handlePasswordReset}
            >
              Изменить
            </div>
          </div>
          <div
            className="passwordResetEditingProfile"
            onClick={() => setOpenEditingProfileModal("info")}
          >
            ← Назад
          </div>
          <svg
            onClick={() => setEditingProfileModal(false)}
            className="closeButtonEditingProfile"
            width="24"
            height="24"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M8.53464 25.3327L6.66797 23.466L14.1346 15.9993L6.66797 8.53268L8.53464 6.66602L16.0013 14.1327L23.468 6.66602L25.3346 8.53268L17.868 15.9993L25.3346 23.466L23.468 25.3327L16.0013 17.866L8.53464 25.3327Z"
              fill="white"
            />
          </svg>
        </>
      ) : null}
    </div>
  )
}
