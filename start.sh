#!/bin/bash

# Start the backend
echo "Starting Python backend..."
(cd buy_sell_algorithm && python main.py) &

# Start the frontend
echo "Starting React frontend..."
(cd react-front-end && npm start) &

# Wait for both processes to complete
wait

#chmod +x start.sh

