import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import database
from datetime import date, timedelta

print("Generating synthetic agricultural dataset...")
crops = ["Rice (Paddy)", "Wheat", "Cotton", "Maize", "Millets"]
n_samples = 2500

data = []
for _ in range(n_samples):
    crop = np.random.choice(crops)
    
    # Synthetic logic representing real-world agricultural requirements
    if crop == "Rice (Paddy)":
        n = np.random.randint(70, 100)
        p = np.random.randint(40, 60)
        k = np.random.randint(30, 50)
        ph = np.random.uniform(5.5, 7.0)
        rain = np.random.uniform(150, 250)
        temp = np.random.uniform(22, 35)
    elif crop == "Wheat":
        n = np.random.randint(60, 90)
        p = np.random.randint(30, 50)
        k = np.random.randint(20, 40)
        ph = np.random.uniform(6.0, 7.5)
        rain = np.random.uniform(50, 100)
        temp = np.random.uniform(15, 25)
    elif crop == "Cotton":
        n = np.random.randint(90, 130)
        p = np.random.randint(30, 60)
        k = np.random.randint(30, 60)
        ph = np.random.uniform(5.8, 8.0)
        rain = np.random.uniform(60, 110)
        temp = np.random.uniform(21, 35)
    elif crop == "Maize":
        n = np.random.randint(80, 120)
        p = np.random.randint(40, 80)
        k = np.random.randint(40, 80)
        ph = np.random.uniform(5.5, 7.5)
        rain = np.random.uniform(60, 120)
        temp = np.random.uniform(18, 28)
    else: # Millets
        n = np.random.randint(20, 50)
        p = np.random.randint(20, 40)
        k = np.random.randint(10, 30)
        ph = np.random.uniform(5.5, 8.5)
        rain = np.random.uniform(30, 60)
        temp = np.random.uniform(25, 40)
        
    data.append([n, p, k, ph, rain, temp, crop])

df = pd.DataFrame(data, columns=['N', 'P', 'K', 'pH', 'Rainfall', 'Temperature', 'Crop'])

print("Training Random Forest Classifier...")
X = df[['N', 'P', 'K', 'pH', 'Rainfall', 'Temperature']]
y = df['Crop']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print(f"Model Training Complete. Validation Accuracy: {accuracy_score(y_test, preds):.2f}")

joblib.dump(model, 'crop_model.pkl')
print("Model dynamically saved as 'crop_model.pkl'.")

# Check if database is empty, seed initial dummy data
if not database.get_expenses():
    print("Seeding SQLite with initial financial data...")
    database.add_expense("Seeds", 2000, str(date.today() - timedelta(days=5)))
    database.add_expense("Fertilizer", 1500, str(date.today() - timedelta(days=2)))
    database.add_expense("Labor", 500, str(date.today()))
    print("Database seeding complete.")
