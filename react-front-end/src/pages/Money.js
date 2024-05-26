import React from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

const Money = () => {
  const data1 = {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    datasets: [
      {
        label: 'First dataset',
        backgroundColor: 'rgba(75,192,192,0.2)',
        borderColor: 'rgba(75,192,192,1)',
        data: [65, 59, 80, 81, 56, 55, 40],
      },
    ],
  };

  const data2 = {
    labels: ['August', 'September', 'October', 'November', 'December'],
    datasets: [
      {
        label: 'Second dataset',
        backgroundColor: 'rgba(153,102,255,0.2)',
        borderColor: 'rgba(153,102,255,1)',
        data: [42, 68, 33, 91, 76],
      },
    ],
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-2xl text-white mb-4">Money</h1>
      <div className="flex w-11/12 md:w-3/4">
        <div className="w-1/2">
          <div className="chart-container mb-8">
            <Line data={data1} />
          </div>
          <div className="chart-container">
            <Line data={data2} />
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
        </div>
      </div>
    </div>
  );
};

export default Money;
