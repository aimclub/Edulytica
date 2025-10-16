import { motion } from "framer-motion"
import "./confirmModal.scss"

/**
 * Модальное окно для подтверждения удаления тикета
 * @param {boolean} props.visible
 * @param {string} props.title
 * @param {string} props.description
 * @param {Function} props.onConfirm
 * @param {Function} props.onCancel
 */
export const ConfirmModal = ({
  visible,
  title,
  description,
  onConfirm,
  onCancel,
}) => {
  if (!visible) return null

  return (
    <div className="confirmModalOverlay" role="dialog" aria-modal="true">
      <motion.div
        className="confirmModal"
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.98 }}
        transition={{ duration: 0.2 }}
      >
        <div className="confirmTitle">{title}</div>
        <div className="confirmDesc">{description}</div>
        <div className="confirmActions">
          <button className="btn cancel" onClick={onCancel}>
            Отмена
          </button>
          <button
            className="btn danger"
            onClick={() => onConfirm && onConfirm()}
          >
            Удалить
          </button>
        </div>
      </motion.div>
    </div>
  )
}
