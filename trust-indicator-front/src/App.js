import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from "./components/Navbar";
import { AuthProvider } from './context/AuthContext';


function App() {

    return (
        <Router>
            <AuthProvider>
                <Navbar />
            </AuthProvider>
        </Router>
    );
}

export default App;
