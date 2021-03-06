# -*- coding: utf-8 -*-
"""Toyota_corolla.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hjOXAenBlX316XzHuaor8tQuEG5kcfrK
"""

import numpy as np
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense, Dropout
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from matplotlib.pylab import rcParams
rcParams['figure.figsize']=15,6

uploaded = files.upload()

df = pd.read_csv('Dataset.csv')

# Separate dates for future plotting
train_dates = pd.to_datetime(df['Date'])

# Variables for taining
# Select the vehicle model which need to predict price
cols = list(df)[1:2]

df_for_training = df[cols].astype(float)

df_for_plot = df_for_training.tail(500)
df_for_plot.plot.line()

# Normalize the dataset
scaler = StandardScaler()
scaler = scaler.fit(df_for_training)
df_for_training_scaled = scaler.transform(df_for_training)

# Training series
trainX = []
# Prediction series
trainY = []

# Number of months we want to predict for future
n_future = 1
# Number of past months we want to use for predict the future
n_past = 14

for i in range(n_past, len(df_for_training_scaled) - n_future +1):
    trainX.append(df_for_training_scaled[i - n_past:i, 
                                         0:df_for_training.shape[1]])
    trainY.append(df_for_training_scaled[i + n_future - 1:i + n_future, 0])

# Convert trainX and trainY into arrays
trainX, trainY = np.array(trainX), np.array(trainY)

print('trainX shape == {}.'.format(trainX.shape))
print('trainY shape == {}.'.format(trainY.shape))

model = Sequential()
model.add(LSTM(64, activation='relu', 
               input_shape=(trainX.shape[1], trainX.shape[2]), 
               return_sequences=True))
model.add(LSTM(32, activation='relu', return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(trainY.shape[1]))

model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
model.summary()

import tensorflow as tf

model.compile(optimizer='sgd', 
              loss=tf.keras.losses.categorical_crossentropy, 
              metrics=['accuracy'])

history = model.fit(trainX, trainY, 
                    epochs=10, 
                    batch_size=10, 
                    validation_split=0.1, 
                    verbose=1)

plt.plot(history.history['accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train'], loc='upper left')
plt.show()

# Forecast
# Start with the last day of training date and predict the future

# Redefining n_future to extend prediction months 
# beyond the original n_future months
n_future = 50
forecast_period_dates = pd.date_range(list(train_dates)[-1],
                                      periods = n_future, 
                                      freq = '1m').tolist()

# Forecast
forecast = model.predict(trainX[-n_future:])

# Inverse transforamtion
forecast_copies = np.repeat(forecast, df_for_training.shape[1], axis=-1)
y_pred_future = scaler.inverse_transform(forecast_copies)[:,0]

# Convert timestamp to date
forecast_dates = []
for time_i in forecast_period_dates:
  forecast_dates.append(time_i.date())

df_forecast = pd.DataFrame({'Date':np.array(forecast_dates),
                            'Toyota_corolla':y_pred_future})
df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])

original = df[['Date', 'Toyota_corolla']]
original['Date'] = pd.to_datetime(original['Date'])
original = original.loc[original['Date'] >= '2015-1-1']

sns.lineplot(original['Date'], 
             original['Toyota_corolla'], 
             label = 'Original data')
sns.lineplot(df_forecast['Date'], 
             df_forecast['Toyota_corolla'], 
             label = 'Predicted data')