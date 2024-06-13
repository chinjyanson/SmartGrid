import React from 'react';
import { Line } from 'react-chartjs-2';

const UsageChart = ({ data }) => {
  return (
    data ? (
      <div className="chart-container mb-8">
        <Line data={data} />
      </div>
    ) : (
      <p className="text-white">Loading usage data...</p>
    )
  );
};

export default UsageChart;
