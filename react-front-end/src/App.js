import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Money from './pages/Money';
import Usage from './pages/Usage';
import './App.css';

const App = () => {
  return (
    <div className="app flex flex-col min-h-screen">
      <Navbar />
      <div className="flex-grow bg-gradient-to-r from-dark-purple to-dark-blue">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/money" element={<Money />} />
          <Route path="/usage" element={<Usage />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
