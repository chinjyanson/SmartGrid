import React from 'react';

const FilterButtons = ({ daysFilter, handleDaysFilterChange }) => {
  return (
    <div className="flex space-x-4 mb-8">
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
  );
};

export default FilterButtons;
