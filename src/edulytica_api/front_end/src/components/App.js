import React from 'react';
import Header from './Header';
import Routes from '../routes/Routes'
import AuthProvider from "../provider/authProvider";
function App() {
    return (
        <AuthProvider>
            <Routes />
        </AuthProvider>
    );
}

export default App;