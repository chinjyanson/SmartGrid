import React from 'react';

const TickBuySell = ({ currentAction, actionLog }) => {
  return (
    <div className="w-full flex flex-col items-center mt-10">
      <div className={`w-full p-5 rounded-lg shadow-lg ${currentAction === 'buy' ? 'bg-green-500' : 'bg-red-500'}`}>
        <h2 className="text-2xl text-white">{currentAction.toUpperCase()}</h2>
      </div>
      <div className="w-full mt-8 bg-gray-200 p-5 rounded-lg shadow-lg">
        <h3 className="text-xl mb-4">Action Log</h3>
        <ul className="overflow-y-auto max-h-40">
          {actionLog.map((log, index) => (
            <li key={index} className="text-sm">{`Tick ${log.tick}: ${log.action} - ${log.value} kWh`}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TickBuySell;
