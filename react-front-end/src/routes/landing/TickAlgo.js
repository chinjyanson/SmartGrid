import React from 'react';
import { Bar, Line } from 'react-chartjs-2';

const TickAlgo = ({ naiveCosts, optimalCosts, naiveCostPerTick, optimalCostPerTick }) => {
  const barChartData = {
    labels: ['Costs'],
    datasets: [
      {
        label: 'Naive Costs',
        data: [naiveCosts],
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
      {
        label: 'Optimal Costs',
        data: [optimalCosts],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const lineChartData = {
    labels: Array.from({ length: 60 }, (_, i) => i), // Labels for ticks 0-59
    datasets: [
      {
        label: 'Naive Cost Per Tick',
        data: naiveCostPerTick,
        fill: true,
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        tension: 0.4,
      },
      {
        label: 'Optimal Cost Per Tick',
        data: optimalCostPerTick,
        fill: true,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="w-full flex flex-col items-center mt-10">
      <div className="w-full mb-8">
        <Bar data={barChartData} />
      </div>
      <div className="w-full">
        <Line data={lineChartData} />
      </div>
    </div>
  );
};

export default TickAlgo;
