// import React, { useState, useEffect } from 'react';
// import raw from '../../assets/TEST_FILE.txt';
// import CurrEnergyUsed from './currEnegyUsed';

// DATA TO SHOW IN THE HOME PAGE:
// 50/50 of buy or sell like speedo with bar chart next to it 1, -1, with pie chart also?
// we also want to show the battery with text inside it showing between 0 to 50 joules of how much is stored, then next to it we will say if this is an increase of X or decrease by X % from the previous tick
// also have a random energy tip of the day put that next to the battery 

import React, { useEffect } from 'react';
import TickEnergy from './TickEnergy';
// import TickBuySell from './TickBuySell';
import TickStorage from './TickStorage';

const Home = () => {
  useEffect(() => {
    document.title = "Home | Smart Grid";
  }, []);
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-3xl text-white">Welcome to the Home Page</h1>
        <TickEnergy />
        {/* <TickStorage /> */}
        {/* <TickBuySell /> */}

    </div>
  );
};

export default Home;