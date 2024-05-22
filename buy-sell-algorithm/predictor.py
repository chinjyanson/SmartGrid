import numpy as np
from scipy.signal import periodogram
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

def predict_next_value(data, num_predictions=1):
    # Step 1: Identify the period using Fourier Transform
    freqs, power = periodogram(data)
    period = 1 / freqs[np.argmax(power)]
    period = int(np.round(period))

    # Step 2: Denoise the signal using moving average
    smoothed_data = np.convolve(data, np.ones(period) / period, mode='valid')

    # Step 3: Fit a sinusoidal model to the periodic component
    t = np.arange(len(smoothed_data))
    A = np.max(smoothed_data) - np.min(smoothed_data)
    phase = 0
    frequency = 2 * np.pi / period
    fitted_periodic = A * np.sin(frequency * t + phase)

    # Step 4: Analyze the residuals for the random component
    residuals = data[:len(fitted_periodic)] - fitted_periodic
    arima_model = ARIMA(residuals, order=(5, 1, 0))
    arima_fit = arima_model.fit()

    # Step 5: Predict the next values
    periodic_prediction = A * np.sin(frequency * (t[-1] + np.arange(1, num_predictions + 1)) + phase)
    random_prediction = arima_fit.forecast(steps=num_predictions)
    combined_prediction = periodic_prediction + random_prediction

    return combined_prediction

# Example usage
data = np.sin(2 * np.pi * np.arange(100) / 20) + np.sin(np.pi * np.arange(100) /40)+ np.random.normal(0, 0.1, 100)
predictions = predict_next_value(data, num_predictions=5)
print(predictions)

# Optional: Plotting the original data and predictions
plt.plot(np.arange(len(data)), data, label='Original Data')
plt.plot(np.arange(len(data), len(data) + len(predictions)), predictions, label='Predictions', linestyle='--')
plt.legend()
plt.show()
