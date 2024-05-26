import React from 'react';

const Battery = ({ level }) => {
  // Ensure the level is between 0 and 100
  const batteryLevel = Math.min(100, Math.max(0, level));

  return (
    <div className="battery">
      <div className="battery-level" style={{ width: `${batteryLevel}%` }}>
        <div className="battery-text">{batteryLevel}%</div>
      </div>
      <div className="battery-cap"></div>
    </div>
  );
};

export default Battery;
