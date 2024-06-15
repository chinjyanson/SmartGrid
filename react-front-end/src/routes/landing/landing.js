// DATA TO SHOW IN THE HOME PAGE:
// 50/50 of buy or sell like speedo with bar chart next to it 1, -1, with pie chart also?
// we also want to show the battery with text inside it showing between 0 to 50 joules of how much is stored, then next to it we will say if this is an increase of X or decrease by X % from the previous tick
// also have a random energy tip of the day put that next to the battery 
// we need to do algorithm comparison so a barchart on the left of naive and optimal, then line graph showing the profit every tick type thing

import React, { useEffect } from 'react';
import EnergySavingTip from './EnergySavingTip';
import TickEnergy from './TickEnergy';
import TickAlgo from './TickAlgo';
import './landing.css'

const Home = () => {
  useEffect(() => {
    document.title = "Home | Smart Grid";
  }, []);

  const scrollToContent = () => {
    const contentSection = document.getElementById('content-section');
    contentSection.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="w-full min-h-screen flex flex-col items-center justify-center">
        <h1 className="text-5xl text-white">Welcome To Your Dashboard</h1>
        <EnergySavingTip />
        <div className="flex flex-col items-center">
          <button onClick={scrollToContent} className="text-white text-xl focus:outline-none hover:scale-110">
            <svg className="w-10 h-10 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
        </div>
      </div>
      <div id="content-section" className="w-full flex flex-col items-center justify-center py-10">
        <div className="w-full mt-8">
          <TickEnergy/>
          <TickAlgo />
          {/* <TickStorage /> */}
          {/* <TickBuySell /> */}
        </div>
      </div>
    </div>
  );
};

export default Home;
