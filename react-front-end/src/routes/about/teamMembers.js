import React from "react";
import Headshot from "../../assets/headshots/headshot.png";
// const teamMembers = [
//     {
//         name: 'Anson Chin',
//         image: 'headshots.jpg',
//         bio: '2nd Year EIE student primarily focused on the development of the algorithm and the hardware software integration of the project',
//     },

//     {
//         name: 'Ilan Iwumbwe',
//         image: 'headshots.jpg',
//         bio: '2nd Year EIE student primarily focused on the development of the ML model for the algorithm and TCP hardware - software communication',
//     }

// ];
const teamMembers = () => {
    return (
        <div>
            {/* <h1 style={{ color: 'white' }}>About</h1>
            <p style={{ color: 'white' }}>Project description goes here...</p> */}
            <div>
                <h2 style={{ color: 'white' }}>Anson Chin</h2>
                <img src={Headshot} alt="Anson Chin" />
                <p style={{ color: 'white' }}>2nd Year EIE student primarily focused on the development of the algorithm and the hardware software integration of the project</p>
            </div>
            <div>
                <h2 style={{ color: 'white' }}>Ilan Iwumbwe</h2>
                <img src={Headshot} alt="Ilan Iwumbwe" />
                <p style={{ color: 'white' }}>2nd Year EIE student primarily focused on the development of the ML model for the algorithm and TCP hardware - software communication</p>
            </div>
        </div>
    );
}

export default teamMembers;

