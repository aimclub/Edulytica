import { useState, useCallback } from "react"

/**
 * Custom hook to handle errors in event handlers
 * Since ErrorBoundary doesn't catch errors in event handlers,
 * this hook provides a way to catch and display them
 */
export const useErrorHandler = () => {
  const [error, setError] = useState(null)
  const [showNotification, setShowNotification] = useState(false)

  const handleError = useCallback((error) => {
    console.error("Error caught by useErrorHandler:", error)

    const message = String(error?.message || "")
    const shouldSkipNotification =
      /could not validate credentials/i.test(message) ||
      /необходима авторизац/i.test(message) ||
      /ошибка сети/i.test(message) ||
      /network error/i.test(message) ||
      /wrong code/i.test(message) ||
      /попробуйте позже/i.test(message) ||
      /try again later/i.test(message) ||
      /validation/i.test(message) ||
      /валидац/i.test(message)

    if (shouldSkipNotification) {
      setShowNotification(false)
      setError(null)
      return
    }

    setError(error)
    setShowNotification(true)

    // Auto-hide notification after 10 seconds
    setTimeout(() => {
      setShowNotification(false)
    }, 10000)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
    setShowNotification(false)
  }, [])

  const safeHandler = useCallback(
    (handler) => {
      return (...args) => {
        try {
          return handler(...args)
        } catch (err) {
          handleError(err)
        }
      }
    },
    [handleError]
  )

  return {
    error,
    showNotification,
    handleError,
    clearError,
    safeHandler,
  }
}
