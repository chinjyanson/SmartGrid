import React from 'react';
import { Line, Pie } from 'react-chartjs-2';

const CombinedCharts = ({ lineChartData, pieChartData }) => (
  <div className="flex flex-wrap">
    <div className="w-full md:w-1/2 p-4">
      <div className="chart-container">
        {lineChartData ? <Line data={lineChartData} /> : <p>Loading line chart data...</p>}
      </div>
    </div>
    <div className="w-full md:w-1/2 p-4">
      <div className="chart-container">
        {pieChartData ? <Pie data={pieChartData} /> : <p>Loading pie chart data...</p>}
      </div>
    </div>
  </div>
);

export default CombinedCharts;
