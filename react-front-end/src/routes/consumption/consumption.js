import React, { useState, useEffect } from 'react';
import axios from 'axios';
import UsageChart from './UsageChart';
import ProductionChart from './ProductionChart';
import GreenScore from './GreenScore';
import FilterButtons from '../../helpers/FilterButtons';

const Consumption = () => {
  const [usageData, setUsageData] = useState(null);
  const [productionData, setProductionData] = useState(null);
  const [daysFilter, setDaysFilter] = useState(90);
  const bigNumber = 12345; // Sample big number

  const fetchUsageData = async () => {
    try {
      const response = await axios.get('https://evuc3y0h1g.execute-api.eu-north-1.amazonaws.com/PROD/accessUsageLog');
      const data = response.data;

      // Sort data by day in ascending order
      const sortedData = data.sort((a, b) => new Date(a.dayID) - new Date(b.dayID));

      const days = sortedData.map(entry => entry.dayID);
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
      const sortedData = data.sort((a, b) => new Date(a.dayID) - new Date(b.dayID));

      const days = sortedData.map(entry => entry.dayID);
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
    document.title = 'Consumption | Smart Grid';
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
      <FilterButtons daysFilter={daysFilter} handleDaysFilterChange={handleDaysFilterChange} />
      <div className="flex w-11/12 md:w-3/4">
        <div className="w-1/2">
          {filteredUsageData ? (
            <UsageChart data={filteredUsageData} />
          ) : (
            <p className="text-white">Loading usage data...</p>
          )}
          {filteredProductionData ? (
            <ProductionChart data={filteredProductionData} />
          ) : (
            <p className="text-white">Loading production data...</p>
          )}
        </div>
        <GreenScore score={bigNumber} />
      </div>
    </div>
  );
};

export default Consumption;
