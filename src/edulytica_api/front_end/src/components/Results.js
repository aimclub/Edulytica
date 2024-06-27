import { Link, useNavigate } from "react-router-dom"
import instance from "../provider/jwtInterceptor"
import '../css/results_list.css'

import React, { useState, useEffect } from 'react';

const Results = (props) => {
  const [results_data, setResults] = useState([]);
  useEffect(() => {
    instance.get(props.url, props.ticket_id)
      .then(response => {
        setResults(response.data)
      })
  }, [])
  return (
    <div>
      <ul className="list1a">
        {results_data.map((el) => (
          <Link to='/result' state={{ticket_id:el.id}}><li key={el.id}>{el.id}</li></Link>
        ))}
      </ul>
    </div>
  )
    ;
};

export default Results;