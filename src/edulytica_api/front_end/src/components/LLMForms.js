import React from "react"
import instance from "../provider/jwtInterceptor"
import '../css/upload.css'

const LLMForm = (props) => {

  async function btn_click() {
    const form = document.getElementById('llm_form')
    const data = new FormData(form)
    return await purposeFile(props.url, data)
  }
  async function purposeFile(url, data) {
    instance.post(url, data)
      .then(response => {
        console.log(response.data)
        // navigate("/", { replace: true });
      })
      .catch(error => console.error(error));
  }
  function updateFileName() {
    const fileInput = document.getElementById('file_input');
    const fileNameSpan = document.getElementById('file_name');

    if (fileInput.files.length > 0) {
      fileNameSpan.textContent = fileInput.files[0].name;
    } else {
      fileNameSpan.textContent = 'Файл не выбран';
    }
  }

  return (

    <div className="fileLoader">
      <div className="fileLoader_wrapper">
        <h1>Прикрепление файла</h1>
        <form id="llm_form">
          <div className="file_upload">

            <label htmlFor="file_input" className="file_label">Выберите файл</label>
            <input name="file" type="file" id="file_input" className="file_input" onChange={updateFileName} multiple/>
            <div className="content">
              <div className="content__container">
                <span id="file_name" className="file_name">Файл не выбран</span>
              </div>
            </div>

          </div>

          <input className="downloadBtn" type="button" value="Отправить" onClick={btn_click} />
        </form>
      </div>

    </div>
  )
    ;
};

export default LLMForm;
