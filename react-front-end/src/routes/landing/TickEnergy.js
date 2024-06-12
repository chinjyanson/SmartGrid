import React, { useState, useEffect } from 'react';
import { Scatter } from 'react-chartjs-2';
import Speedometer from 'react-d3-speedometer';
import 'chart.js/auto';

const TickEnergy = () => {
  const [energyUsage, setEnergyUsage] = useState(50);
  const [energyProduced, setEnergyProduced] = useState(50);
  const [tickCount, setTickCount] = useState(0);
  const [chartData, setChartData] = useState({
    labels: Array.from({ length: 60 }, (_, i) => i), // Create labels from 0 to 59
    datasets: [
      {
        label: 'Energy Usage (kWh)',
        data: Array.from({ length: 60 }, (_, i) => ({ x: i, y: null })), // Create an array with 60 objects with x and y properties for energy usage
        borderColor: 'rgba(75,192,192,1)',
        backgroundColor: 'rgba(75,192,192,0.2)',
        pointBackgroundColor: 'rgba(255, 192, 203, 0.8)', // Lighter pink color for energy usage points
        pointBorderColor: 'rgba(255, 150, 150, 0.6)',
      },
      {
        label: 'Energy Produced (kWh)',
        data: Array.from({ length: 60 }, (_, i) => ({ x: i, y: null })), // Create an array with 60 objects with x and y properties for energy produced
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        pointBackgroundColor: 'rgba(64, 224, 208, 0.8)', // Slightly darker pastel bluish green color for energy produced points
        pointBorderColor: 'rgba(0, 100, 90, 0.6)',
      },
    ],
  });

  useEffect(() => {
    const updateData = () => {
      const newUsageValue = (Math.random() * 100).toFixed(2); // Generate a random value between 0 and 100 for energy usage
      setEnergyUsage(newUsageValue);

      const newProducedValue = (Math.random() * 100).toFixed(2); // Generate a random value between 0 and 100 for energy produced
      setEnergyProduced(newProducedValue);

      setChartData(prevData => {
        let newUsageData = [...prevData.datasets[0].data];
        let newProducedData = [...prevData.datasets[1].data];

        // Add the new values to the data at the current tick
        newUsageData[tickCount] = { x: tickCount, y: newUsageValue };
        newProducedData[tickCount] = { x: tickCount, y: newProducedValue };

        // Clear data after 59 ticks and reset tick count to 0
        if (tickCount >= 59) {
          newUsageData = Array.from({ length: 60 }, (_, i) => ({ x: i, y: null }));
          newProducedData = Array.from({ length: 60 }, (_, i) => ({ x: i, y: null }));
          setTickCount(0); // Reset tick count
        } else {
          setTickCount(prevCount => prevCount + 1); // Increment tick count
        }

        return {
          ...prevData,
          datasets: [
            {
              ...prevData.datasets[0],
              data: newUsageData,
            },
            {
              ...prevData.datasets[1],
              data: newProducedData,
            },
          ],
        };
      });
    };

    const interval = setInterval(updateData, 5000); // Update data every 5 seconds

    return () => clearInterval(interval); // Clean up interval on unmount
  }, [tickCount]);

  return (
    <div className="w-full flex justify-center mt-10">
      <div className="bg-gray-500 bg-opacity-50 p-7 rounded-lg shadow-lg w-11/12 flex items-center">
        <div className="flex flex-col items-center mr-8"> {/* Added margin to separate speedometers */}
          <div className="flex flex-col items-center mb-20"> {/* Added margin bottom to separate speedometers */}
            <Speedometer
              value={energyUsage}
              minValue={0}
              maxValue={100}
              needleColor="white"
              startColor="pink"
              segments={10}
              endColor="purple"
              width={300} // Adjusted size of the speedometer
              height={200} // Adjusted size of the speedometer
              textColor="transparent" // Hide the number inside the speedometer
            />
            <p className="text-lg">Current Energy Usage: <strong>{energyUsage} kWh</strong></p> {/* Bold the current energy usage line */}
          </div>
          <div className="flex flex-col items-center"> {/* Added margin bottom to separate speedometers */}
            <Speedometer
              value={energyProduced}
              minValue={0}
              maxValue={100}
              needleColor="white"
              startColor="#3498db"
              segments={10}
              endColor="#2ecc71"
              width={300} // Adjusted size of the speedometer
              height={200} // Adjusted size of the speedometer
              textColor="transparent" // Hide the number inside the speedometer
            />
            <p className="text-lg">Current Energy Produced: <strong>{energyProduced} kWh</strong></p> {/* Bold the current energy produced line */}
          </div>
        </div>
        <div className="w-full"> {/* Updated the width to take remaining space */}
          <Scatter
            data={chartData}
            options={{
              scales: {
                x: {
                  title: {
                    display: true,
                    text: 'Ticks',
                    color: 'white',
                  },
                  type: 'linear',
                  position: 'bottom',
                  min: 0,
                  max: 59,
                  ticks: {
                    stepSize: 1,
                    color: 'white',
                  },
                  grid: {
                    color: 'rgba(0, 0, 0, 0.1)',
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: 'Energy (kWh)',
                    color: 'white',
                  },
                  type: 'linear',
                  position: 'left',
                  min: 0,
                  max: 100,
                  ticks: {
                    color: 'white',
                  },
                  grid: {
                    color: 'rgba(0, 0, 0, 0.1)',
                  },
                },
              },
              plugins: {
                legend: {
                  labels: {
                    color: 'white',
                  },
                },
              },
            }}
          />
        </div>
      </div>
    </div>
  );
} 

export default TickEnergy;
