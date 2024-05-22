import React from 'react'

function Navbar() {
  return (
    <div className='navbar'>
        <div className='navbar-logo'>
            <h1>Logo</h1>
        </div>
        <ul className='navbar-menu'> // replace with icons in the future and relocate this 
            <li>Home</li>  
            <li>About</li>
            <li>Contact</li>
        </ul>
    </div>
  )
}

export default Navbar