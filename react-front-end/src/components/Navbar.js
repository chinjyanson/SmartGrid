import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar h-16 w-full bg-gray-800 text-white flex items-center justify-center">
      <ul className="flex space-x-4">
        <li>
          <Link to="/" className="text-lg">Home</Link>
        </li>
        <li>
          <Link to="/money" className="text-lg">Money</Link>
        </li>
        <li>
          <Link to="/usage" className="text-lg">Usage</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
