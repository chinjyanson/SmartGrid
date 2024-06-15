import React from 'react';
import { Bar } from 'react-chartjs-2';

const BarChart = ({ data }) => (
  <div className="chart-container">
    {data ? <Bar data={data} /> : <p>Loading earnings data...</p>}
  </div>
);

export default BarChart;
