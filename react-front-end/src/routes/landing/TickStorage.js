import React, { useState, useEffect } from 'react';
import './TickStorage.css';

const TickStorage = () => {
  const [batteryPercentage, setBatteryPercentage] = useState(50);

  useEffect(() => {
    const updateBattery = () => {
      const newPercentage = Math.floor(Math.random() * 96) + 5; // Random value between 5 and 100
      setBatteryPercentage(newPercentage);
    };

    const interval = setInterval(updateBattery, 5000); // Update battery percentage every 5 seconds

    return () => clearInterval(interval); // Clean up interval on unmount
  }, []);

  return (
    <div className="battery-container">
      <div className="battery">
        <div className="liquid" style={{ height: `${batteryPercentage}%` }}></div>
        <div className="cap"></div>
        <div className="terminal"></div>
        <div className="terminal"></div>
      </div>
    </div>
  );
};

export default TickStorage;
