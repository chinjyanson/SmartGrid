import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import Speedometer from 'react-d3-speedometer';

// make a pie chart that grows to 59 to show the ratio of buy to sell?

const TickBuySell = () => {
  const [ticks, setTicks] = useState([]);
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Buy/Sell Decisions',
        data: [],
        backgroundColor: [],
      },
    ],
  });

  useEffect(() => {
    const updateChartData = (decision) => {
      const newData = [...chartData.datasets[0].data];
      const newLabels = [...chartData.labels];

      if (ticks.length >= 59) {
        // Clear chart data if there are 59 ticks
        setTicks([]);
        setChartData((prevData) => ({
          ...prevData,
          labels: [],
          datasets: [
            {
              ...prevData.datasets[0],
              data: [],
            },
          ],
        }));
      } else {
        setTicks((prevTicks) => [...prevTicks, decision]);

        newData.push(decision > 0 ? decision : 0);
        newLabels.push(newLabels.length + 1);
        const backgroundColor = decision > 0 ? 'rgba(75, 192, 192, 0.2)' : 'rgba(255, 99, 132, 0.2)';

        setChartData((prevData) => ({
          ...prevData,
          labels: newLabels,
          datasets: [
            {
              ...prevData.datasets[0],
              data: newData,
              backgroundColor: backgroundColor,
            },
          ],
        }));
      }
    };

    // Simulate buy/sell decisions
    const interval = setInterval(() => {
      const decision = Math.random() > 0.5 ? 1 : -1; // Randomly decide between buy (1) and sell (-1)
      updateChartData(decision);
    }, 1000);

    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, [chartData]);

  return (
    <div className="w-full flex justify-around mt-10">
      <div className="w-1/3 flex justify-center items-center">
        <Speedometer
          value={ticks.length > 0 ? (ticks[ticks.length - 1] === 1 ? 100 : 0) : 50} // Set speedometer value based on the last tick
          needleColor={ticks.length > 0 ? (ticks[ticks.length - 1] === 1 ? 'green' : 'red') : 'gray'} // Set needle color based on the last tick
          startColor='red'
          segments={2}
          endColor='green'
          valueFormatter={() => (ticks.length > 0 ? (ticks[ticks.length - 1] === 1 ? 135 : 45) : 90)} // Set the angle of the needle
          currentValueText={ticks.length > 0 ? (ticks[ticks.length - 1] === 1 ? 'Buy' : 'Sell') : ''}
        />
      </div>
      <div className="w-2/3">
        <Bar data={chartData} />
      </div>
    </div>
  );
};

export default TickBuySell;
