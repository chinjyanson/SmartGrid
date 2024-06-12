import React from 'react';
import logo from '../assets/renewable-energy.png';
import { Link, NavLink } from 'react-router-dom';
import { ResetLocation } from '../helpers/reset-location.js';
import { FaBell } from 'react-icons/fa';

const Navbar = () => {
  return (
    <header>
      <nav className="navbar h-20 w-full bg-gray-800 text-white flex items-center px-4">
        <NavLink
          onClick={() => {
            ResetLocation();
          }}
          to="/"
          className="flex items-center space-x-3"
        >
          <img
            width="50"
            height="50"
            className="logo"
            src={logo}
            alt="Sun Logo"
          />
          <h1 className="text-xl font-semibold">
            <span>Smart Grid</span>
          </h1>
        </NavLink>
        <ul className="flex space-x-6 ml-auto">
          <li>
            <Link to="/" className="text-lg hover:text-gray-300">
              Home
            </Link>
          </li>
          <li>
            <Link to="/finances" className="text-lg hover:text-gray-300">
              Finances
            </Link>
          </li>
          <li>
            <Link to="/consumption" className="text-lg hover:text-gray-300">
              Consumption
            </Link>
          </li>
          <li className="flex items-center space-x-1">
            <Link to="/about" className="text-lg hover:text-gray-300">
              About
            </Link>
          </li>
          {/* <li>
            <FontAwesomeIcon icon="fa-regular fa-bell" />
          </li> */}
        </ul>
      </nav>
    </header>
  );
};

export default Navbar;
