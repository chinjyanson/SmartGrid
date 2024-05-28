import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

const Usage = () => {
  const [usageData, setUsageData] = useState(null);
  const [productionData, setProductionData] = useState(null);
  const [daysFilter, setDaysFilter] = useState(90);

  const fetchUsageData = async () => {
    try {
      const response = await axios.get('https://evuc3y0h1g.execute-api.eu-north-1.amazonaws.com/PROD/accessUsageLog');
      const data = response.data;

      // Sort data by day in ascending order
      const sortedData = data.sort((a, b) => new Date(a.day) - new Date(b.day));

      const days = sortedData.map(entry => entry.day);
      const energyUsed = sortedData.map(entry => entry.energyUsed);

      setUsageData({
        labels: days,
        datasets: [
          {
            label: 'Energy Used',
            data: energyUsed,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
          },
        ],
      });
    } catch (error) {
      console.error('Error fetching usage data', error);
    }
  };

  const fetchProductionData = async () => {
    try {
      const response = await axios.get('https://evuc3y0h1g.execute-api.eu-north-1.amazonaws.com/PROD/accessEnergyLog');
      const data = response.data;

      // Sort data by day in ascending order
      const sortedData = data.sort((a, b) => new Date(a.day) - new Date(b.day));

      const days = sortedData.map(entry => entry.day);
      const energyProduced = sortedData.map(entry => entry.energyProduced);
      const avgSunIrradiance = sortedData.map(entry => entry.avgSunIrradiance);

      setProductionData({
        labels: days,
        datasets: [
          {
            label: 'Energy Produced',
            data: energyProduced,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
          },
          {
            label: 'Avg Sun Irradiance',
            data: avgSunIrradiance,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
          },
        ],
      });
    } catch (error) {
      console.error('Error fetching production data', error);
    }
  };

  useEffect(() => {
    fetchUsageData();
    fetchProductionData();
  }, []);

  const filterData = (data, days) => {
    const endIndex = data.labels.length;
    const startIndex = Math.max(0, endIndex - days);
    return {
      ...data,
      labels: data.labels.slice(startIndex, endIndex),
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        data: dataset.data.slice(startIndex, endIndex),
      })),
    };
  };

  const handleDaysFilterChange = (days) => {
    setDaysFilter(days);
  };

  const filteredUsageData = usageData ? filterData(usageData, daysFilter) : null;
  const filteredProductionData = productionData ? filterData(productionData, daysFilter) : null;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-2xl text-white mb-4">Usage</h1>
      <div className="flex space-x-4 mb-4">
        {['1 Day', '3 Days', '7 Days', '30 Days', '90 Days'].map((label, index) => {
          const days = parseInt(label.split(' ')[0], 10);
          return (
            <button
              key={index}
              className={`px-4 py-2 rounded ${daysFilter === days ? 'bg-blue-700 text-white' : 'bg-gray-500 text-gray-100'} hover:bg-blue-300 hover:text-black`}
              onClick={() => handleDaysFilterChange(days)}
            >
              {label}
            </button>
          );
        })}
      </div>
      <div className="flex w-11/12 md:w-3/4">
        <div className="w-1/2">
          {filteredUsageData ? (
            <div className="chart-container mb-8">
              <Line data={filteredUsageData} />
            </div>
          ) : (
            <p className="text-white">Loading usage data...</p>
          )}
          {filteredProductionData ? (
            <div className="chart-container">
              <Line data={filteredProductionData} />
            </div>
          ) : (
            <p className="text-white">Loading production data...</p>
          )}
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

export default Usage;
