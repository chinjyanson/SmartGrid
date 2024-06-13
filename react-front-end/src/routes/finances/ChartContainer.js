import React from 'react';
import { Line, Bar } from 'react-chartjs-2';

const ChartContainer = ({ topChartData, bottomChartData }) => {
  return (
    <div className="w-1/2">
      {topChartData ? (
        <div className="chart-container mb-8">
          <Line data={topChartData} />
        </div>
      ) : (
        <p className="text-white">Loading chart data...</p>
      )}
      {bottomChartData ? (
        <div className="chart-container">
          <Bar data={bottomChartData} />
        </div>
      ) : (
        <p className="text-white">Loading earnings data...</p>
      )}
    </div>
  );
};

export default ChartContainer;
