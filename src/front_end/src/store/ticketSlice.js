import { createSlice } from "@reduxjs/toolkit"
import { ticketService } from "../services/ticket.service"

// Глобальные объекты для хранения активных интервалов опроса
const activePolls = {}
const activeDocumentPolls = {}

// Получаем начальное состояние из localStorage или используем дефолтное
const getInitialState = () => {
  const savedState = localStorage.getItem("ticketState")
  if (savedState) {
    try {
      return JSON.parse(savedState)
    } catch (e) {
      console.error("Ошибка при парсинге сохраненного состояния тикета:", e)
    }
  }
  return {
    currentTicket: null,
    tickets: [],
    loading: false,
    error: null,
  }
}

const ticketSlice = createSlice({
  name: "ticket",
  initialState: getInitialState(),
  reducers: {
    setCurrentTicket: (state, action) => {
      state.currentTicket = action.payload
      // Сохраняем состояние в localStorage
      localStorage.setItem("ticketState", JSON.stringify(state))
    },
    setTickets: (state, action) => {
      state.tickets = action.payload
      localStorage.setItem("ticketState", JSON.stringify(state))
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
    clearTicketState: (state) => {
      state.currentTicket = null
      state.tickets = []
      state.loading = false
      state.error = null
      localStorage.removeItem("ticketState")
      // Останавливаем все активные опросы при выходе
      Object.keys(activePolls).forEach((ticketId) => {
        clearInterval(activePolls[ticketId])
        delete activePolls[ticketId]
      })
      Object.keys(activeDocumentPolls).forEach((ticketId) => {
        clearInterval(activeDocumentPolls[ticketId])
        delete activeDocumentPolls[ticketId]
      })
    },
  },
})

// Thunk для получения истории тикетов
export const fetchTicketHistory = () => async (dispatch) => {
  try {
    dispatch(setLoading(true))
    const ticketHistory = await ticketService.getTicketHistory()
    dispatch(setTickets(ticketHistory))
    return ticketHistory
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// Thunk для получения данных конкретного тикета
export const fetchTicket = (ticketId) => async (dispatch) => {
  try {
    dispatch(setLoading(true))
    const ticketInfo = await ticketService.getTicket(ticketId)
    const ticketStatus = await ticketService.getTicketStatus(ticketId)
    const ticketData = {
      ticketId: ticketInfo.ticket.id,
      ticketInfo: ticketInfo.ticket,
      status: ticketStatus.status,
    }
    dispatch(setCurrentTicket(ticketData))

    // Загружаем исходный документ сразу
    try {
      await dispatch(fetchDocumentText(ticketId))
    } catch (error) {
      console.error("Ошибка при загрузке исходного документа:", error)
      // Если не удалось загрузить сразу, запускаем опрос
      dispatch(startPollingForDocument(ticketId))
    }

    // Если тикет в обработке, запускаем опрос
    if (
      ticketData.status === "In progress" ||
      ticketData.status === "Created"
    ) {
      dispatch(startPollingForTicket(ticketId))
    }

    return ticketData
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// Thunk для создания нового тикета
export const createTicket =
  (file, eventId, mega_task_id) => async (dispatch) => {
    try {
      dispatch(setLoading(true))
      const data = await ticketService.createNewTicket(
        file,
        eventId,
        mega_task_id
      )
      // После создания тикета, загружаем его данные и запускаем опрос
      await dispatch(fetchTicket(data.ticket_id))
      return data.ticket_id
    } catch (error) {
      dispatch(setError(error.message))
      throw error
    } finally {
      dispatch(setLoading(false))
    }
  }

// Загрузка только исходного документа
export const fetchDocumentText = (ticketId) => async (dispatch, getState) => {
  try {
    dispatch(setLoading(true))

    const documentResponse = await ticketService.getDocumentText(ticketId)
    const file = documentResponse.text || ""

    // Обновляем текущий тикет с загруженным исходным документом
    const prev = getState().ticket.currentTicket
    dispatch(
      setCurrentTicket({
        ...prev,
        files: {
          ...prev.files,
          file,
        },
      })
    )

    // Если документ успешно загружен, останавливаем опрос
    if (file) {
      dispatch(stopPollingForDocument(ticketId))
    }

    return { file }
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// Загрузка только результата
export const fetchResultText = (ticketId) => async (dispatch, getState) => {
  try {
    dispatch(setLoading(true))

    const resultResponse = await ticketService.getResultText(ticketId)
    const result = resultResponse.text || ""

    // Обновляем текущий тикет с загруженным результатом
    const prev = getState().ticket.currentTicket
    dispatch(
      setCurrentTicket({
        ...prev,
        files: {
          ...prev.files,
          result,
        },
      })
    )

    return { result }
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// Загрузка обоих файлов (оставляем для обратной совместимости)
export const fetchTicketFiles = (ticketId) => async (dispatch, getState) => {
  try {
    dispatch(setLoading(true))

    // Получаем текст напрямую с новых эндпоинтов
    const [documentResponse, resultResponse] = await Promise.all([
      ticketService.getDocumentText(ticketId),
      ticketService.getResultText(ticketId),
    ])

    const file = documentResponse.text || ""
    const result = resultResponse.text || ""

    // Обновляем текущий тикет с загруженными строками
    const prev = getState().ticket.currentTicket
    dispatch(
      setCurrentTicket({
        ...prev,
        files: {
          file,
          result,
        },
      })
    )

    return { file, result }
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// --- Логика опроса ---

const pollTicketStatus = (ticketId) => async (dispatch, getState) => {
  try {
    const ticketStatus = await ticketService.getTicketStatus(ticketId)
    const { currentTicket } = getState().ticket

    // Обновляем статус в текущем тикете, если он открыт
    if (currentTicket && currentTicket.ticketId === ticketId) {
      dispatch(
        setCurrentTicket({ ...currentTicket, status: ticketStatus.status })
      )
    }

    // Если обработка завершена, останавливаем опрос и загружаем только результат
    if (ticketStatus.status === "Completed") {
      dispatch(stopPollingForTicket(ticketId))
      dispatch(fetchResultText(ticketId))
    }
  } catch (error) {
    console.error(`Ошибка опроса для тикета ${ticketId}:`, error)
    dispatch(stopPollingForTicket(ticketId)) // Останавливаем при ошибке
  }
}

export const startPollingForTicket = (ticketId) => (dispatch) => {
  if (activePolls[ticketId]) {
    return // Уже опрашивается
  }
  const intervalId = setInterval(() => {
    dispatch(pollTicketStatus(ticketId))
  }, 2000)
  activePolls[ticketId] = intervalId
}

export const stopPollingForTicket = (ticketId) => () => {
  if (activePolls[ticketId]) {
    clearInterval(activePolls[ticketId])
    delete activePolls[ticketId]
  }
}

// Функция для опроса исходного документа
const pollDocumentText = (ticketId) => async (dispatch, getState) => {
  try {
    const documentResponse = await ticketService.getDocumentText(ticketId)
    const file = documentResponse.text || ""

    // Обновляем текущий тикет с загруженным исходным документом
    const prev = getState().ticket.currentTicket
    dispatch(
      setCurrentTicket({
        ...prev,
        files: {
          ...prev.files,
          file,
        },
      })
    )

    // Если документ успешно загружен, останавливаем опрос
    if (file) {
      dispatch(stopPollingForDocument(ticketId))
    }
  } catch (error) {
    console.error(
      `Ошибка опроса исходного документа для тикета ${ticketId}:`,
      error
    )
    // Не останавливаем опрос при ошибке, продолжаем пытаться
  }
}

export const startPollingForDocument = (ticketId) => (dispatch) => {
  if (activeDocumentPolls[ticketId]) {
    return // Уже опрашивается
  }
  const intervalId = setInterval(() => {
    dispatch(pollDocumentText(ticketId))
  }, 2000)
  activeDocumentPolls[ticketId] = intervalId
}

export const stopPollingForDocument = (ticketId) => () => {
  if (activeDocumentPolls[ticketId]) {
    clearInterval(activeDocumentPolls[ticketId])
    delete activeDocumentPolls[ticketId]
  }
}

export const {
  setCurrentTicket,
  setTickets,
  setLoading,
  setError,
  clearTicketState,
} = ticketSlice.actions

export default ticketSlice.reducer
