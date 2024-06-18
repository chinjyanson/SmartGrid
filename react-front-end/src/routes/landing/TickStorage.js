import React from 'react';
import { Doughnut, Bar } from 'react-chartjs-2';

const TickStorage = ({ currentStorage, storageChange, historicalStorage }) => {
  const doughnutData = {
    labels: ['Stored', 'Remaining'],
    datasets: [
      {
        data: [currentStorage, 50 - currentStorage],
        backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
        borderWidth: 1,
      },
    ],
  };

  const barChartData = {
    labels: Array.from({ length: 60 }, (_, i) => i),
    datasets: [
      {
        label: 'Historical Storage',
        data: historicalStorage,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="w-full flex flex-col items-center mt-10">
      <div className="w-full mb-8 flex flex-col items-center">
        <Doughnut data={doughnutData} />
        <p className="text-lg mt-2">Current Storage: {currentStorage.toFixed(2)}%</p>
        <p className={`text-lg mt-2 ${storageChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
          Storage Change: {storageChange.toFixed(2)}%
        </p>
      </div>
      <div className="w-full mb-8 flex flex-col items-center">
        <Bar data={barChartData} />
      </div>
    </div>
  );
};

export default TickStorage;
