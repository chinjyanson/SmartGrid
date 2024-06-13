import React from 'react';

const GreenScore = ({ score }) => {
  return (
    <div className="w-1/2 text-white ml-8 flex flex-col items-center justify-start">
      <h2 className="text-2xl mb-4">Your Green Score</h2>
      <h2 className="text-6xl font-bold mb-8">{score}</h2>
      <div className="text-left w-full px-4">
        {/* Additional content can go here */}
      </div>
    </div>
  );
};

export default GreenScore;
