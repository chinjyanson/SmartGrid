import React from 'react';

const WeeklyComparison = ({ comparison }) => (
  <div className="weekly-comparison">
    <h2>Weekly Comparison</h2>
    <p>Energy Bought: {comparison.energyBought.difference.toFixed(2)} kWh ({comparison.energyBought.trend})</p>
    <p>Energy Sold: {comparison.energySold.difference.toFixed(2)} kWh ({comparison.energySold.trend})</p>
    <p>Costs: ${comparison.earnings.difference.toFixed(2)} ({comparison.earnings.trend})</p>
  </div>
);

export default WeeklyComparison;
