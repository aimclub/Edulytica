import { useNavigate } from "react-router-dom"
import instance from "../provider/jwtInterceptor"
import { useLocation } from 'react-router-dom'
import React, { useState, useEffect } from 'react';
import '../css/detail_result.css'
import { saveAs } from 'file-saver'

const DetailResult = (props) => {

  const navigate = useNavigate();
  const location = useLocation()
  const { ticket_id } = location.state
  const [results_data, setResults] = useState();
  useEffect(() => {
    instance.post(props.url, { 'id': ticket_id })
      .then(response => {
        setResults(response.data)
      })
  }, [])

  function get_file() {
    const url = 'http://localhost:8000/llm/file/' + results_data.ticket.result_files[0].id
    instance.get(url)
      .then(response => saveAs(
        new Blob(
          [JSON.stringify(response.data, null, 2)],
          { type: "application/json;charset=" + document.characterSet }
        ), "file.json"))
  }
  return (
    <div className="result_div">
      <section className="mainSection">
        <nav>
          <ul classNameName="information">
            <div className="information_text__wrapper">
              <div className="loaderStatus">
                <div className="loader"></div>
                <label className="mainSectionLabel_wrapper" for="status">Статус:</label>
              </div>
              <li><div className="mainSectionLabel">{results_data && results_data.ticket.status.status}</div></li>
              <div className="loaderTask">
                <div className="typeTask"></div>
                <label className="mainSectionLabel_wrapper" for="type">Тип задачи:</label>
              </div>
              <li><div className="mainSectionLabel">{results_data && results_data.ticket.ticket_type}</div></li>
            </div>

            <li className="textGap"><div><input className="downloadBtn" type="button" name="download" classNameName="form-styling" value='Скачать' onClick={get_file}/></div></li>
          </ul>
        </nav>

        <article>
          <textarea placeholder="Цель данной работы" cols='60' classNameName="result_area goal" readonly value={results_data && results_data.result_data.goal}> </textarea>
          <textarea classNameName="result_area result" readonly value={results_data && results_data.result_data.result}></textarea>
        </article>
      </section>
    </div>
  )
    ;
};

export default DetailResult;