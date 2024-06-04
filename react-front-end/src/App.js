import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/navbar.js';
import Home from './routes/landing/landing';
import Money from './routes/finances/finances.js';
import Usage from './routes/consumption/consumption.js';
import NotFound from './routes/not-found/not-found.js';
import './core-ui/App.css';

const App = () => {
  return (
    <div className="app flex flex-col min-h-screen">
      <Navbar />
      <div className="flex-grow bg-gradient-to-r from-dark-purple to-dark-blue">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/money" element={<Money />} />
          <Route path="/usage" element={<Usage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
