import { useEffect, useState } from "react"
import { Input } from "../../utils/input/input"
import "./editingProfile.scss"
export const EditingProfile = ({
  setEditingProfileModal,
  infoProfile,
  setInfoProfile,
}) => {
  const [openEditingProfileModal, setOpenEditingProfileModal] = useState("info")
  const [localProfile, setLocalProfile] = useState(infoProfile)
  const handleChangeInfo = (e) => {
    const { name, value } = e.target
    setLocalProfile((prev) => ({ ...prev, [name]: value }))
    console.log("Обновленный профиль:", localProfile)
  }

  useEffect(() => {
    setLocalProfile(infoProfile)
  }, [infoProfile])

  const handleEditingProfileModal = () => {
    setOpenEditingProfileModal("info")
    setInfoProfile(localProfile)
    setEditingProfileModal(false)
  }
  return (
    <div className="editingProfile">
      {openEditingProfileModal === "info" ? (
        <>
          <div className="titleEditingProfile">Профиль</div>
          <div className="containerEditingProfile">
            <div className="inputContainerEditingProfile">
              <div className="blockInputEditingProfile">
                <div className="titleInputEditingProfile">Имя</div>
                <Input
                  type="text"
                  placeholder={
                    infoProfile.name !== "..." && infoProfile.name !== ""
                      ? infoProfile.name
                      : "Введите ваше имя..."
                  }
                  name="name"
                  onChange={handleChangeInfo}
                />
              </div>
              <div className="blockInputEditingProfile">
                <div className="titleInputEditingProfile">Фамилия</div>
                <Input
                  type="text"
                  placeholder={
                    infoProfile.surname !== "..." && infoProfile.surname !== ""
                      ? infoProfile.surname
                      : "Введите вашу фамилию..."
                  }
                  name="surname"
                  onChange={handleChangeInfo}
                />
              </div>
              <div className="blockInputEditingProfile">
                <div className="titleInputEditingProfile">Дата рождения</div>
                <Input
                  type="text"
                  placeholder={
                    infoProfile.birthday !== "..." &&
                    infoProfile.birthday !== " "
                      ? infoProfile.birthday
                      : "Введите дату рождения..."
                  }
                  onChange={handleChangeInfo}
                  name="birthday"
                />
              </div>
            </div>
            <div
              className="btnBottomEditingProfile"
              onClick={handleEditingProfileModal}
            >
              <svg
                width="18"
                height="19"
                viewBox="0 0 18 19"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M6.83109 4.31C7.48359 4.115 8.20359 3.9875 8.99859 3.9875C12.5911 3.9875 15.5011 6.8975 15.5011 10.49C15.5011 14.0825 12.5911 16.9925 8.99859 16.9925C5.40609 16.9925 2.49609 14.0825 2.49609 10.49C2.49609 9.155 2.90109 7.91 3.59109 6.875M8.06859 2L5.90109 4.49L8.42859 6.335"
                  stroke="#BEBABA"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              Изменить
            </div>
          </div>
          <div
            className="passwordResetEditingProfile"
            onClick={() => setOpenEditingProfileModal("password")}
          >
            Сбросить пароль
            <svg
              width="16"
              height="10"
              viewBox="0 0 21 15"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M13.2034 14.0228L19.9903 7.83603L13.2228 1.62808M1.00965 7.80637L19.8005 7.83573"
                stroke="#B4B4B4"
                stroke-width="1.75"
                stroke-miterlimit="10"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
          <svg
            onClick={() => setEditingProfileModal(false)}
            style={{
              position: "absolute",
              top: "40px",
              right: "40px",
              cursor: "pointer",
            }}
            width="32"
            height="32"
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
            <div className="inputContainerEditingProfile">
              <div className="blockInputEditingProfile">
                <div className="titleInputEditingProfile">Старый пароль</div>
                <Input type="password" placeholder="Введите старый пароль..." />
              </div>
              <div className="blockInputEditingProfile">
                <div className="titleInputEditingProfile">
                  Введите новый пароль
                </div>
                <Input type="password" placeholder="Введите новый пароль..." />
              </div>
              <div className="blockInputEditingProfile">
                <div className="titleInputEditingProfile">
                  Введите повторно новый пароль
                </div>
                <Input
                  type="password"
                  placeholder="Введите повторно новый пароль..."
                />
              </div>
            </div>
            <div
              className="btnBottomEditingProfile"
              onClick={handleEditingProfileModal}
            >
              <svg
                width="18"
                height="19"
                viewBox="0 0 18 19"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M6.83109 4.31C7.48359 4.115 8.20359 3.9875 8.99859 3.9875C12.5911 3.9875 15.5011 6.8975 15.5011 10.49C15.5011 14.0825 12.5911 16.9925 8.99859 16.9925C5.40609 16.9925 2.49609 14.0825 2.49609 10.49C2.49609 9.155 2.90109 7.91 3.59109 6.875M8.06859 2L5.90109 4.49L8.42859 6.335"
                  stroke="#BEBABA"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              Изменить
            </div>
          </div>
          <svg
            onClick={() => setEditingProfileModal(false)}
            style={{
              position: "absolute",
              top: "40px",
              right: "40px",
              cursor: "pointer",
            }}
            width="32"
            height="32"
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
