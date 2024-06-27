import React, { useState, useEffect } from 'react';
import '../css/headers.css'
import { useAuth } from "../provider/authProvider";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import logo from '../images/logo.svg';

const Header = () => {
    const [active, setActive] = useState()
    const { token } = useAuth();

    useEffect(() => {
        // Update the document title using the browser API
        setActive(window.location.pathname)
    });


    return (
        <header className="header">
            <div className="wrap-logo">
                <img src={logo} height="30" />
            </div>
            <div>
                <Link to="/" className={active === '/' ? 'active' : 'deactive'} onClick={() => setActive('/')}>Главная</Link>
                {token && <Link to="/results" className={active === '/results' ? 'active' : 'deactive'} onClick={() => setActive('/results')}>Результаты</Link>}
                {token && <Link to="/purpose" className={active === '/purpose' ? 'active' : 'deactive'} onClick={() => setActive('/purpose')}>Достижимость целей и задач</Link>}
                {token && <Link to="/summarize" className={active === '/summarize' ? 'active' : 'deactive'} onClick={() => setActive('/summarize')}>Суммаризация</Link>}
                <Link to="/contact" className={active === '/contact' ? 'active' : 'deactive'} onClick={() => setActive('/contact')}>Контакты</Link>
                <Link to="/about" className={active === '/about' ? 'active' : 'deactive'} onClick={() => setActive('/about')}>О нас</Link>
                {!token && <Link to="/login" className={active === '/login' ? 'active' : 'deactive'} onClick={() => setActive('/login')}>Вход</Link>}
                {token && <Link to="/logout" className={active === '/logout' ? 'active' : 'deactive'}>Выход</Link>}
            </div>
        </header >
    )


}

export default Header