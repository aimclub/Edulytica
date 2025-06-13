import { useEffect, useState } from "react"
import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"
import { motion } from "framer-motion"
import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
import { ResultFile } from "../../components/resultFile/resultFile"
import { EditingProfile } from "../../components/editingProfile/editingProfile"
import { AddEvent } from "../../components/addEvent/addEvent"
import { useSelector, useDispatch } from "react-redux"
import { fetchUserData } from "../../store/authSlice"
import { ticketService } from "../../services/ticket.service"

/**
 *  * Компонент страницы аккаунта пользователя.
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.accountModal - Флаг, определяющий, отображается ли модальное окно аккаунта
 * @param {function} props.setAccountModal - Функция для установки значения флага отображения модального окна аккаунта
 * @param {boolean} props.profileModal - Флаг, определяющий, отображается ли модальное окно профиля
 * @param {function} props.setProfileModal - Функция для установки значения флага отображения модального окна профиля
 * @param {string} props.accountSection - Текущая секция аккаунта ("main", "result" и т. д.).
 * @param {function} props.setAccountSection - Функция для обновления текущей секции аккаунта.
 * @returns {JSX.Element} Страница аккаунта пользователя
 */

export const Account = ({
  accountModal,
  setAccountModal,
  profileModal,
  setProfileModal,
  accountSection,
  setAccountSection,
  isAuth,
}) => {
  const dispatch = useDispatch()
  const [selectedParams, setSelectedParams] = useState([]) // массив для хранения параметров при отправки документа
  const [fileResult, setFileResult] = useState("")
  const [editingProfileModal, setEditingProfileModal] = useState(false)
  const [editingProfileAnimation, setEditingProfileAnimation] = useState(false)
  const [addEventModal, setAddEventModal] = useState(false)
  const [tickets, setTickets] = useState([])

  // Получаем данные пользователя из Redux store
  const userData = useSelector((state) => state.auth.currentUser)
  console.log("Current user data from Redux:", userData)

  useEffect(() => {
    dispatch(fetchUserData())
  }, [dispatch])

  const [infoProfile, setInfoProfile] = useState({
    name: userData?.name || "...",
    surname: userData?.surname || "...",
    login: userData?.login || "...",
    organization: userData?.organization || "...",
  })

  // Обновляем infoProfile при изменении данных пользователя
  useEffect(() => {
    console.log("User data changed, updating infoProfile:", userData)
    if (userData) {
      setInfoProfile({
        name: userData.name || "...",
        surname: userData.surname || "...",
        login: userData.login || "...",
        organization: userData.organization || "...",
      })
    }
  }, [userData])

  const [event, setEvent] = useState([
    { name: "ППС", info: "Это описание мероприятия ППС" },
    { name: "КМУ", info: "Это описание мероприятия КМУ" },
  ])
  const [key, setKey] = useState(0)

  useEffect(() => {
    console.log(event)
  }, [event])

  useEffect(() => {
    setKey((prevKey) => prevKey + 1)
  }, [accountSection])

  useEffect(() => {
    if (addEventModal) {
      setTimeout(() => setEditingProfileAnimation(true), 10)
    } else {
      setEditingProfileAnimation(false)
    }
  }, [addEventModal])

  useEffect(() => {
    if (editingProfileModal) {
      setTimeout(() => setEditingProfileAnimation(true), 10)
    } else {
      setEditingProfileAnimation(false)
    }
  }, [editingProfileModal])

  const fetchTicketHistory = async () => {
    try {
      const ticketHistory = await ticketService.getTicketHistory()
      setTickets(ticketHistory)
    } catch (err) {
      console.log(err)
    }
  }

  return (
    <div className="accPage">
      <Header
        isAuth={isAuth}
        setAccountModal={setAccountModal}
        setProfileModal={setProfileModal}
      />
      <div className="containerAddFile">
        {accountModal ? (
          <AccountModal
            setAccountSection={setAccountSection}
            accountSection={accountSection}
            setFileResult={setFileResult}
            tickets={tickets}
            fetchTicketHistory={fetchTicketHistory}
          />
        ) : null}
        <div className="addFileAccPageAnimate">
          <motion.div
            key={key}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            {accountSection === "main" ? (
              <div className={`addFileAccPage ${accountModal ? "shift" : ""}`}>
                <AddFile
                  setAccountSection={setAccountSection}
                  selectedParams={selectedParams}
                  setSelectedParams={setSelectedParams}
                  setFileResult={setFileResult}
                  setAddEventModal={setAddEventModal}
                  event={event}
                  fetchTicketHistory={fetchTicketHistory}
                />
              </div>
            ) : accountSection === "result" ? (
              <div className={`addFileAccPage ${accountModal ? "shift" : ""}`}>
                <ResultFile fileName={fileResult} />
              </div>
            ) : null}{" "}
          </motion.div>
        </div>
      </div>
      <div className={`profileModalAccPage ${profileModal ? "visible" : ""}`}>
        {profileModal && (
          <ProfileModal
            setProfileModal={setProfileModal}
            setEditingProfileModal={setEditingProfileModal}
            infoProfile={infoProfile}
          />
        )}
      </div>
      {editingProfileModal && (
        <>
          <div className="editingProfileOverlay" />
          <div
            className={`editingProfileModalWrapper ${
              editingProfileAnimation ? "show" : ""
            }`}
          >
            <EditingProfile
              setEditingProfileModal={() => setEditingProfileModal(false)}
              infoProfile={infoProfile}
              setInfoProfile={setInfoProfile}
            />
          </div>
        </>
      )}
      {addEventModal && (
        <>
          <div className="editingProfileOverlay" />
          <div
            className={`editingProfileModalWrapper ${
              editingProfileAnimation ? "show" : ""
            }`}
          >
            <AddEvent
              setAddEventModal={setAddEventModal}
              event={event}
              setEvent={setEvent}
            />
          </div>
        </>
      )}
    </div>
  )
}
