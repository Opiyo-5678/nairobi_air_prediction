# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import SimpleExpSmoothing
from sklearn.metrics import mean_absolute_error
import pickle

file_path = "set-data.csv"
# Step 1: Load and preprocess the data
def load_data(file_path):
    df = pd.read_csv(file_path)
# df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y %H:%M')
    df.set_index('date', inplace=True)
    return df

# Step 2: Visualize the data
def visualize_data(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['value'], label="value", marker='o')
    plt.xlabel("Date")
    plt.ylabel("value (µg/m³)")
    plt.title("value Levels in Nairobi (2019)")
    plt.legend()
    plt.grid()
    plt.show()

# Step 3: Train and evaluate the model
def train_and_evaluate(df):
    # Split the data into training and testing sets
    train_size = int(len(df) * 0.8)  # 80% for training
    train_data = df.iloc[:train_size]
    test_data = df.iloc[train_size:]

    # Train the simple exponential smoothing model
    model = SimpleExpSmoothing(train_data['value'])
    fitted_model = model.fit()

    # Forecast for the testing data
    forecast = fitted_model.forecast(steps=len(test_data))

    # Evaluate the model's performance
    mae = mean_absolute_error(test_data['value'], forecast)
    print(f"Mean Absolute Error (MAE): {mae}")

    # Plot the results
    plt.figure(figsize=(12, 6))
    plt.plot(train_data.index, train_data['value'], label="Training Data", marker='o')
    plt.plot(test_data.index, test_data['value'], label="Actual Testing Data", marker='o')
    plt.plot(test_data.index, forecast, label="Forecasted Data", marker='x')
    plt.xlabel("Date")
    plt.ylabel("value (µg/m³)")
    plt.title("value Forecast Using Simple Exponential Smoothing")
    plt.legend()
    plt.grid()
    plt.show()

    return fitted_model

# Step 4: Save the trained model
def save_model(model, file_path):
    with open(file_path, "wb") as file:
        pickle.dump(model, file)

# Step 5: Load the trained model and make predictions
def load_model(file_path):
    with open(file_path, "rb") as file:
        model = pickle.load(file)
    return model

def make_predictions(model, steps=5):
    forecast = model.forecast(steps=steps)
    print(f"Forecasted value for the next {steps} days:")
    print(forecast)

# Main function to run the entire pipeline
def main():
    # Step 1: Load and preprocess the data
    file_path = "set-data.csv"
    df = load_data(file_path)

    # Step 2: Visualize the data
    visualize_data(df)

    # Step 3: Train and evaluate the model
    fitted_model = train_and_evaluate(df)

    # Step 4: Save the trained model
    model_file_path = "value_forecast_model.pkl"
    save_model(fitted_model, model_file_path)

    # Step 5: Load the trained model and make predictions
    loaded_model = load_model(model_file_path)
    make_predictions(loaded_model, steps=5)

# Run the main function
if __name__ == "__main__":
    main()