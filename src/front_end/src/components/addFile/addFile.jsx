import "./addFile.scss"
/**
 *
 * @returns {JSX.Element} block for attaching and working with a file
 */
export const AddFile = () => {
  return (
    <div className="addFile">
      <div className="titleAddFile">Начните работу над документом</div>
      <div className="blockAddFile">
        <div className="textBlockAddFile">
          Выберите параметры работы над документом...
        </div>
        <div className="parametersLineAddFile">
          <div className="rightparametersLineAddFile">
            <div className="parameterBtnAddFile">
              <svg
                width="17"
                height="17"
                viewBox="0 0 17 17"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M8.5013 3.54102V13.4577M3.54297 8.49935H13.4596"
                  stroke="#89AAFF"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              Прикрепить
            </div>
            <div className="parameterBtnAddFile">
              <svg
                width="12"
                height="11"
                viewBox="0 0 12 11"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M5.83791 2.3144C6.04905 3.5794 7.14895 4.54648 8.51402 4.67481M1.47266 10.0831H10.3112M6.51062 1.64981L2.47927 5.63273C2.32705 5.78398 2.17974 6.0819 2.15028 6.28815L1.9686 7.77315C1.90476 8.3094 2.31723 8.67607 2.88682 8.5844L4.46793 8.33232C4.6889 8.29565 4.99825 8.1444 5.15047 7.98857L9.18182 4.00565C9.87908 3.31815 10.1933 2.5344 9.10816 1.57648C8.0279 0.627731 7.20788 0.962314 6.51062 1.64981Z"
                  stroke="#89AAFF"
                  stroke-width="1.5"
                  stroke-miterlimit="10"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              Мероприятие
            </div>
            <div className="parameterBtnAddFile">
              <svg
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M16.5 7.5V11.25C16.5 15 15 16.5 11.25 16.5H6.75C3 16.5 1.5 15 1.5 11.25V6.75C1.5 3 3 1.5 6.75 1.5H10.5M16.5 7.5H13.5C11.25 7.5 10.5 6.75 10.5 4.5V1.5M16.5 7.5L10.5 1.5M5.25 9.75H9.75M5.25 12.75H8.25"
                  stroke="#89AAFF"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              Справочник
            </div>
          </div>
          <svg
            className="svgParameterBtnAddFile"
            width="18"
            height="18"
            viewBox="0 0 18 18"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M13.5542 7.1775L9.00172 2.625L4.44922 7.1775M9.00172 15.375V2.7525"
              stroke="#303030"
              stroke-width="1.75"
              stroke-miterlimit="10"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
      </div>
    </div>
  )
}
