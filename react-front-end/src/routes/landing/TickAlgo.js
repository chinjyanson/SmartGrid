import React from 'react';
import { Bar, Line } from 'react-chartjs-2';

const TickAlgo = ({ currNaiveCosts, currOptimalCosts, naiveCosts, optimalCosts, storageCosts, naiveCostPerTick, optimalCostPerTick, storageCostPerTick }) => {
  const barChartData = {
    labels: ['Costs'],
    datasets: [
      {
        label: 'Current Naive Cost',
        data: [naiveCosts],
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
      {
        label: 'Current Optimal Cost',
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
        label: 'Naive Costs',
        data: naiveCostPerTick,
        fill: true,
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
        tension: 0.4,
      },
      {
        label: 'Optimal Costs',
        data: optimalCostPerTick,
        fill: true,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
        tension: 0.4,
      },
      {
        label: 'Optimal Costs + Potential Storage Sales',
        data: storageCostPerTick,
        fill: true,
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 2,
        tension: 0.4,
      },
    ],
  };

  const lineChartOptions = {
    scales: {
      x: {
        title: {
          display: true,
          text:'Ticks',
          color: 'white', // X axis title color
          font: {
            weight: 'bold', // Make the title bold
          },
        },
        ticks: {
          color: 'white', // X axis ticks color
        },
      },
      y: {
        title: {
          display: true,
          text:'Costs ($)',
          color: 'white', // X axis title color
          font: {
            weight: 'bold', // Make the title bold
          },
        },
        ticks: {
          color: 'white', // Y axis ticks color
        },
      },
    },
    plugins:{
      legend: {
        labels: {
          color: 'white',
        },
      },
    },
  };

  const performanceComparison = ((optimalCosts - naiveCosts) / naiveCosts * 100).toFixed(2);

  return (
<div className="w-full flex flex-col items-center mt-10">
      <div className="bg-gray-500 bg-opacity-50 p-7 rounded-lg shadow-lg w-11/12 flex flex-col items-center">
        <div className="w-full flex items-center">
          <div className="w-full flex-1">
            <Bar data={barChartData} />
          </div>
          <div className="w-full flex-3">
            <Line data={lineChartData} options={lineChartOptions} />
          </div>
        </div>
        <div className="algo-info shadow-2xl mt-5 flex justify-between space-x-5">
          <p className="text-lg text-gray-800">
            Total Naive Cost: <span className="font-bold">${naiveCosts.toFixed(2)}</span>
          </p>
          <p className="text-lg text-gray-800">
            Total Optimal Cost: <span className="font-bold">${optimalCosts.toFixed(2)}</span>
          </p>
          <p className="text-lg text-gray-800">
            Total Optimal Cost Combined with Storage Sales: <span className="font-bold">${storageCosts.toFixed(2)}</span>
          </p>
        </div>
        <p className="italic text-sm items-center mt-5">
          "A positive cost is the amount paid by the user, while a negative cost indicates a profit that is accounted for the user."
        </p>
      </div>
    </div>
  );
};

export default TickAlgo;
