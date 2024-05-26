import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import Battery from '../components/Battery';

const Usage = () => {
  const [currentGraph, setCurrentGraph] = useState('dataset1');

  const data1 = {
    labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    datasets: [
      {
        label: 'First dataset',
        backgroundColor: 'rgba(255,99,132,0.2)',
        borderColor: 'rgba(255,99,132,1)',
        data: [12, 19, 3, 5, 2],
      },
    ],
  };

  const data2 = {
    labels: ['Saturday', 'Sunday', 'Monday', 'Tuesday'],
    datasets: [
      {
        label: 'Second dataset',
        backgroundColor: 'rgba(54,162,235,0.2)',
        borderColor: 'rgba(54,162,235,1)',
        data: [23, 17, 10, 5],
      },
    ],
  };

  const handleLabelClick = (dataset) => {
    setCurrentGraph(dataset);
  };

  const currentData = currentGraph === 'dataset1' ? data1 : data2;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-2xl text-white mb-4">Usage</h1>
      <div className="flex w-11/12 md:w-3/4">
        <div className="w-1/2">
          <div className="chart-container mb-8">
            <Line data={currentData} />
          </div>
          <div className="flex space-x-4">
            <button
              className={`px-4 py-2 ${currentGraph === 'dataset1' ? 'bg-blue-500' : 'bg-gray-500'} text-white rounded`}
              onClick={() => handleLabelClick('dataset1')}
            >
              First dataset
            </button>
            <button
              className={`px-4 py-2 ${currentGraph === 'dataset2' ? 'bg-blue-500' : 'bg-gray-500'} text-white rounded`}
              onClick={() => handleLabelClick('dataset2')}
            >
              Second dataset
            </button>
          </div>
        </div>
        <div className="w-1/2 text-white ml-8">
          <h2 className="text-xl mb-4">Analysis</h2>
          <p className="mb-4">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum vel dolor et diam gravida tempus.
            Integer ac interdum urna. Quisque pulvinar, nulla eu tristique vehicula, lorem eros aliquet turpis,
            vel luctus nisl mauris et turpis.
          </p>
          <p className="mb-4">
            Donec id augue vel nisl dignissim pharetra. Curabitur eget vehicula purus. Aliquam erat volutpat.
            Phasellus eu est at libero ullamcorper fringilla. Etiam a eros at ex convallis scelerisque.
          </p>
          <p className="mb-4">
            Suspendisse potenti. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.
            Fusce vehicula massa nec magna cursus, a tincidunt odio efficitur.
          </p>
          <Battery level={75} />
        </div>
      </div>
    </div>
  );
};

export default Usage;
