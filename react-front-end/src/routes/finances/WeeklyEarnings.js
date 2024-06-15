import React from 'react';

const WeeklyEarnings = ({ earnings }) => (
  <div className="earnings-counter">
    <h2>Weekly Costs:</h2>
    <p>${earnings.toFixed(2)}</p>
  </div>
);

export default WeeklyEarnings;
