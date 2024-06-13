import React from 'react';
import { Line } from 'react-chartjs-2';

const ProductionChart = ({ data }) => {
  return (
    data ? (
      <div className="chart-container mb-8">
        <Line data={data} />
      </div>
    ) : (
      <p className="text-white">Loading production data...</p>
    )
  );
};

export default ProductionChart;
