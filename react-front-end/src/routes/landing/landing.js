import React, { useState, useEffect } from 'react';
import raw from '../../assets/TEST_FILE.txt';
import { Line } from 'react-chartjs-2';
import Speedometer from 'react-d3-speedometer';

// DATA TO SHOW IN THE HOME PAGE:
// 50/50 of buy or sell like speedo with bar chart next to it 1, -1
// Current energy in with a graph
// Front End API Call? 

const Home = () => {
  const [fileContent, setFileContent] = useState('');
  const [energyValue, setEnergyValue] = useState(50);
  const [chartData, setChartData] = useState({
    labels: ['0', '1', '2', '3', '4', '5'],
    datasets: [
      {
        label: 'Energy Usage (kWh)',
        data: [65, 59, 80, 81, 56, 55],
        borderColor: 'rgba(75,192,192,1)',
        backgroundColor: 'rgba(75,192,192,0.2)',
      },
    ],
  });

  useEffect(() => {
    document.title = 'Home | Smart Grid';

    fetch(raw)
      .then((r) => r.text())
      .then((text) => {
        setFileContent(text);
      });

    // Change energy value every 5 seconds
    const energyInterval = setInterval(() => {
      setEnergyValue(Math.floor(Math.random() * 100));
    }, 5000);

    // Update chart data every 5 seconds
    const chartInterval = setInterval(() => {
      setChartData(prevData => {
        const newLabels = [...prevData.labels, `${prevData.labels.length}`];
        const newData = [...prevData.datasets[0].data, Math.floor(Math.random() * 100)];
        
        return {
          ...prevData,
          labels: newLabels,
          datasets: [{
            ...prevData.datasets[0],
            data: newData,
          }],
        };
      });
    }, 5000);

    // Clean up intervals on component unmount
    return () => {
      clearInterval(energyInterval);
      clearInterval(chartInterval);
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-3xl text-white">Welcome to the Home Page</h1>
      <pre className="text-white">{fileContent}</pre>
      <div className="w-full flex justify-around mt-10">
        <div className="w-1/3 flex justify-center items-center">
          <Speedometer
            value={energyValue}
            minValue={0}
            maxValue={100}
            needleColor="red"
            startColor="green"
            segments={10}
            endColor="blue"
            currentValueText={`Current Energy Usage: ${energyValue} kWh`}
          />
        </div>
        <div className="w-2/3">
          <Line data={chartData} />
        </div>
      </div>
    </div>
  );
};

export default Home;
