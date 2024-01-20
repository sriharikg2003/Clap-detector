from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, Bidirectional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import confusion_matrix, classification_report
from plot_cm import plot_confusion_matrix


df = pd.read_pickle("srihari_final_audio_data_csv/audio_data.csv")

input_features = df["feature"].values
input_features = np.concatenate(input_features, axis=0).reshape(len(input_features), -1)
labels = np.array(df["class_label"].tolist())
labels = to_categorical(labels)

X_train, X_test, y_train, y_test = train_test_split(input_features, labels, test_size=0.3, random_state=42)

model = Sequential([
    LSTM(128, input_shape=(X_train.shape[1], 1), return_sequences=True),
    Dropout(0.3),
    Bidirectional(LSTM(128, return_sequences=True)),
    Dropout(0.3),
    Bidirectional(LSTM(128)),
    Dropout(0.3),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(2, activation='softmax')
])

print(model.summary())

model.compile(
    loss="categorical_crossentropy",
    optimizer='adam',
    metrics=['accuracy']
)

print("Model Score: \n")
history = model.fit(X_train, y_train, epochs=50)

model.save("srihari_saved_model/WWD4.h5")

test_score = model.evaluate(X_test, y_test)
print(test_score)

print("Model Classification Report: \n")
y_pred = np.argmax(model.predict(X_test), axis=1)
conf_matrix = confusion_matrix(np.argmax(y_test, axis=1), y_pred)
print(classification_report(np.argmax(y_test, axis=1), y_pred))

plot_confusion_matrix(conf_matrix, classes=["NO CLAP", "CLAP"])
