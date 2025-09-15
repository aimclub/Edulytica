import { useEffect, useState, useCallback, useRef } from "react"
import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"
import { motion } from "framer-motion"
import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
import { ResultFile } from "../../components/resultFile/resultFile"
import { EditingProfile } from "../../components/editingProfile/editingProfile"
import { AddEvent } from "../../components/addEvent/addEvent"
import { NotificationModal } from "../../components/notificationModal/notificationModal"
import { useSelector, useDispatch } from "react-redux"
import store from "../../store/store"
import { fetchUserData } from "../../store/authSlice"
import {
  fetchTicket,
  fetchTicketHistory,
  setCurrentTicket,
  setTickets,
  startPollingForTicket,
  stopPollingForTicket,
  fetchDocumentText,
  startPollingForDocument,
} from "../../store/ticketSlice"
import { useLocation, useNavigate } from "react-router-dom"

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
  const location = useLocation()
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const [selectedParams, setSelectedParams] = useState([
    { type: "mode", name: "рецензирование" },
  ]) // массив для хранения параметров при отправки документа
  const [editingProfileModal, setEditingProfileModal] = useState(false)
  const [editingProfileAnimation, setEditingProfileAnimation] = useState(false)
  const [addEventModal, setAddEventModal] = useState(false)
  const [notificationModal, setNotificationModal] = useState({
    visible: false,
    text: "",
    eta: "",
  })
  const [resultReadyModal, setResultReadyModal] = useState({
    visible: false,
    text: "",
  })
  const [previousUrl, setPreviousUrl] = useState(null)
  const isFirstRender = useRef(true)
  const notificationTimeoutRef = useRef(null)
  const hasNavigatedAway = useRef(false)
  const isPageRefresh = useRef(false)

  const userData = useSelector((state) => state.auth.currentUser)
  const { currentTicket, tickets } = useSelector((state) => state.ticket)

  useEffect(() => {
    dispatch(fetchUserData())
  }, [dispatch])

  // Load ticket history on component mount
  useEffect(() => {
    dispatch(fetchTicketHistory())
  }, [dispatch])

  // Обновляем секцию аккаунта на основе URL
  useEffect(() => {
    const path = location.pathname
    const currentUrl = `${path}?${new URLSearchParams(
      location.search
    ).toString()}`

    // Определяем, произошел ли переход на другую страницу
    // Не считаем навигацией обновление страницы
    const isNavigationAway =
      previousUrl && previousUrl !== currentUrl && !isPageRefresh.current

    // Закрываем уведомления только при переходе на страницы, отличные от /account/result
    if (path !== "/account/result") {
      // Очищаем таймер уведомлений
      if (notificationTimeoutRef.current) {
        clearTimeout(notificationTimeoutRef.current)
        notificationTimeoutRef.current = null
      }
      setNotificationModal({ visible: false, text: "", eta: "" })
      setResultReadyModal({ visible: false, text: "" })
    }

    if (path === "/account/result") {
      setAccountSection("result")
      // Получаем ticketId из параметров URL
      const searchParams = new URLSearchParams(location.search)
      const ticketId = searchParams.get("ticketId")
      const currentUrl = `${path}?${searchParams.toString()}`

      // Закрываем уведомления при переходе между разными результатами
      if (isNavigationAway && previousUrl.includes("/account/result")) {
        // Очищаем таймер уведомлений
        if (notificationTimeoutRef.current) {
          clearTimeout(notificationTimeoutRef.current)
          notificationTimeoutRef.current = null
        }
        setNotificationModal({ visible: false, text: "", eta: "" })
        setResultReadyModal({ visible: false, text: "" })
      }

      setPreviousUrl(currentUrl)

      if (ticketId) {
        // Получаем актуальные данные из store
        const state = store.getState()
        const { tickets: currentTickets, currentTicket: currentTicketState } =
          state.ticket

        // Проверяем, есть ли тикет в истории пользователя
        const foundTicket = currentTickets.find((t) => t.id === ticketId)

        if (foundTicket) {
          // Тикет найден в истории - это наш тикет
          if (
            !currentTicketState ||
            currentTicketState.ticketId !== foundTicket.id
          ) {
            ;(async () => {
              try {
                await dispatch(fetchTicket(foundTicket.id))
              } catch (e) {
                // Если тикет из истории недоступен - перенаправляем на главную
                if (
                  e?.response?.status === 400 ||
                  e?.response?.status === 403 ||
                  e?.response?.status === 404 ||
                  e?.response?.status === 422
                ) {
                  navigate("/account", { replace: true })
                }
              }
            })()
          }
        } else {
          // Тикет не найден в истории - это может быть чужой публичный тикет
          // Пытаемся загрузить его напрямую
          ;(async () => {
            try {
              console.log("Attempting to load ticket:", ticketId)
              console.log("Current user ID:", userData?.id)
              const result = await dispatch(fetchTicket(ticketId))
              if (result && result.ticketId) {
                // Проверяем, является ли загруженный тикет чужим
                const ticketData = result.ticketInfo
                if (ticketData && ticketData.user_id !== userData?.id) {
                  // Проверяем, нет ли уже такого временного тикета в истории
                  const existingTempTicket = currentTickets.find(
                    (t) => t.id === ticketId && t.isTemporary
                  )

                  if (!existingTempTicket) {
                    // Это чужой тикет - НЕ добавляем его в историю
                    // Временный тикет будет только в currentTicket
                    console.log(
                      "Temporary ticket loaded, not adding to history:",
                      ticketData.id
                    )
                  } else {
                  }
                }
              }
            } catch (e) {
              console.error("Failed to load ticket:", e)
              console.error("Error details:", {
                status: e?.response?.status,
                data: e?.response?.data,
                message: e?.message,
              })
              // Если тикет недоступен - перенаправляем на главную
              if (
                e?.response?.status === 400 ||
                e?.response?.status === 403 ||
                e?.response?.status === 404 ||
                e?.response?.status === 422
              ) {
                console.warn(
                  "Ticket is not accessible:",
                  e?.response?.data?.detail || e.message
                )
                // Очищаем URL от неправильного ticketId
                navigate("/account", { replace: true })
              } else {
                console.warn("Ticket loaded but with errors:", e)
                // Для других ошибок тоже перенаправляем на главную
                navigate("/account", { replace: true })
              }
            }
          })()
        }
      }
    } else if (path === "/account/help") {
      setAccountSection("help")
    } else if (path === "/account/info") {
      setAccountSection("info")
    } else if (path === "/account") {
      setAccountSection("main")
    }
  }, [
    location.pathname,
    location.search,
    setAccountSection,
    dispatch,
    previousUrl,
  ])

  // Показ статусов будем инициировать по клику в истории тикетов

  // Опрос статуса тикета только если открыт result и статус In progress/Created
  useEffect(() => {
    if (
      location.pathname === "/account/result" &&
      currentTicket &&
      (currentTicket.status === "In progress" ||
        currentTicket.status === "Created")
    ) {
      dispatch(startPollingForTicket(currentTicket.ticketId))
      return () => {
        dispatch(stopPollingForTicket(currentTicket.ticketId))
      }
    } else if (currentTicket) {
      // Если уходим с result — останавливаем polling
      dispatch(stopPollingForTicket(currentTicket.ticketId))
    }
  }, [location.pathname, currentTicket, dispatch])

  // Уведомления по статусу показываются по клику из AccountModal

  // Закрываем уведомления при уходе со страницы результата
  useEffect(() => {
    if (
      location.pathname !== "/account/result" &&
      (notificationModal.visible || resultReadyModal.visible)
    ) {
      setNotificationModal({ visible: false, text: "", eta: "" })
      setResultReadyModal({ visible: false, text: "" })
    }
  }, [location.pathname, notificationModal.visible, resultReadyModal.visible])

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

  const [key, setKey] = useState(0)

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

  const handleTicketCreated = useCallback(
    async (ticketData) => {
      console.log("Создан тикет:", ticketData)
      dispatch(setCurrentTicket(ticketData))

      // Принудительно загружаем исходный документ для нового тикета
      try {
        await dispatch(fetchDocumentText(ticketData.ticketId))
      } catch (error) {
        console.error("Ошибка при загрузке исходного документа:", error)
        // Если не удалось загрузить сразу, запускаем опрос
        dispatch(startPollingForDocument(ticketData.ticketId))
      }

      const searchParams = new URLSearchParams(window.location.search)
      searchParams.set("ticketId", ticketData.ticketId)
      window.history.replaceState(null, "", `?${searchParams.toString()}`)

      const modeItem = selectedParams?.find((p) => p.type === "mode")
      const modeName = (modeItem?.name || "").toLowerCase()
      const eta = modeName.includes("анализ")
        ? "≈ 2 мин"
        : modeName.includes("реценз")
        ? "≈ 5 мин"
        : ""
      setTimeout(() => {
        setNotificationModal({
          visible: true,
          text: "Ваш запрос принят в обработку",
          eta,
        })
      }, 500)
    },
    [dispatch, selectedParams]
  )

  const handleFetchTicketHistory = useCallback(() => {
    dispatch(fetchTicketHistory())
  }, [dispatch])

  const handleCloseNotification = useCallback(() => {
    setNotificationModal({ visible: false, text: "", eta: "" })
  }, [])

  const handleCloseResultReady = useCallback(() => {
    setResultReadyModal({ visible: false, text: "" })
  }, [])

  // Показ уведомления о статусе при клике в истории тикетов
  const handleTicketClickNotification = useCallback((ticket) => {
    if (!ticket) return
    // Небольшая задержка, чтобы успела примениться смена URL/секции
    setTimeout(() => {
      const state = store.getState()
      const current = state?.ticket?.currentTicket
      const status = current?.status || ticket.status

      if (status === "Completed") {
        setResultReadyModal({ visible: true, text: "Тикет готов" })
      } else if (status === "Created" || status === "In progress") {
        setResultReadyModal({
          visible: true,
          text: "Результат еще не готов, ожидайте",
        })
      } else if (!status) {
        setResultReadyModal({ visible: false, text: "" })
      } else {
        setResultReadyModal({ visible: false, text: "" })
      }
    }, 300)
  }, [])

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
            tickets={tickets}
            fetchTicketHistory={handleFetchTicketHistory}
            currentTicket={currentTicket}
            onTicketClick={handleTicketClickNotification}
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
                  setAddEventModal={setAddEventModal}
                  addEventModal={addEventModal}
                  fetchTicketHistory={handleFetchTicketHistory}
                  onTicketCreated={handleTicketCreated}
                />
              </div>
            ) : accountSection === "result" ? (
              <div className={`addFileAccPage ${accountModal ? "shift" : ""}`}>
                <ResultFile
                  fileName={currentTicket?.ticketInfo?.name || ""}
                  ticketData={currentTicket}
                  resetSection={currentTicket?.ticketId}
                />
              </div>
            ) : null}
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
              fetchTicketHistory={handleFetchTicketHistory}
            />
          </div>
        </>
      )}
      <NotificationModal
        visible={notificationModal.visible}
        text={notificationModal.text}
        eta={notificationModal.eta}
        onClose={handleCloseNotification}
      />
      <NotificationModal
        visible={resultReadyModal.visible}
        text={resultReadyModal.text}
        eta=""
        onClose={handleCloseResultReady}
        centered={resultReadyModal.text === "Результат еще не готов, ожидайте"}
      />
    </div>
  )
}
