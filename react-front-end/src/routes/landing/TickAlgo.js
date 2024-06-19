import React from 'react';
import { Bar, Line } from 'react-chartjs-2';

const TickAlgo = ({ naiveCosts, optimalCosts, naiveCostPerTick, optimalCostPerTick, storageCostPerTick }) => {
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
        grid: {
          color: 'rgba(255, 255, 255, 0.1)', // Y axis grid lines color
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

  return (
    <div className="w-full flex flex-col items-center mt-10">
      <div className="bg-gray-500 bg-opacity-50 p-7 rounded-lg shadow-lg w-11/12 flex items-center">

        <div className="w-full mb-8 flex-1">
          <Bar data={barChartData} />
        </div>
        <div className="w-full flex-3">
          <Line data={lineChartData} options={lineChartOptions} />
        </div>
        {/* <div className="w-full mt-5 flex justify-between algo-info">
          <p className="text-lg text-gray-800">test</p>
          <p className="text-lg text-gray-800">test</p>
        </div> */}
      </div>
    </div>
  );
};

export default TickAlgo;
