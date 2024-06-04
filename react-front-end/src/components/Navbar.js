import React from 'react';
import logo from '../assets/renewable-energy.png';
import { Link, NavLink } from 'react-router-dom';
import { ResetLocation } from '../helpers/reset-location.js';

const Navbar = () => {
  return (
    <header>
      <nav className="navbar h-16 w-full bg-gray-800 text-white flex items-center justify-start">
        <NavLink
          onClick={() => {
            ResetLocation();
          }}
          to="/"
          className="logo-styling flex-container flex-row txt-center txt-white"
        >
          <img
            width="50"
            height="50"
            className="logo"
            src={logo}
            alt="Sun Logo"
          />
          <h1>
            <span>Smart Grid</span>
          </h1>
        </NavLink>
        <ul className="flex space-x-4 ml-auto">
          <li>
            <Link to="/" className="text-lg">
              Home
            </Link>
          </li>
          <li>
            <Link to="/money" className="text-lg">
              Finances
            </Link>
          </li>
          <li>
            <Link to="/usage" className="text-lg">
              Consumption
            </Link>
          </li>
          <li>
            <Link to="/about" className="text-lg">
              About
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Navbar;
