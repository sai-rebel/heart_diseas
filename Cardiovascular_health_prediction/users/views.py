
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from .models import UserRegistrationModel

import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

import matplotlib
matplotlib.use('Agg')  # Avoids GUI errors for plots
import matplotlib.pyplot as plt

# ================================
# Dropdown Choices for Categorical Features
# ================================
CP_CHOICES = [
    (0, 'Typical Angina'),
    (1, 'Atypical Angina'),
    (2, 'Non-Anginal Pain'),
    (3, 'Asymptomatic')
]

RESTECG_CHOICES = [
    (0, 'Normal'),
    (1, 'ST-T Abnormality'),
    (2, 'Left Ventricular Hypertrophy')
]

SLOPE_CHOICES = [
    (0, 'Upsloping'),
    (1, 'Flat'),
    (2, 'Downsloping')
]

THAL_CHOICES = [
    (0, 'Unknown'),
    (1, 'Fixed Defect'),
    (2, 'Reversible Defect'),
    (3, 'Normal')
]

# ================================
# Index Page
# ================================
def index(request):
    return render(request, "index.html")

# ================================
# User Registration
# ================================
def UserRegisterActions(request):
    if request.method == 'POST':
        user = UserRegistrationModel(
            name=request.POST['name'],
            loginid=request.POST['loginid'],
            password=request.POST['password'],
            mobile=request.POST['mobile'],
            email=request.POST['email'],
            locality=request.POST['locality'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            status='waiting'
        )
        user.save()
        messages.success(request, "Registration successful!")
    return render(request, 'UserRegistrations.html')

# ================================
# User Login
# ================================
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid)
            if check.password == pswd:
                if check.status == "activated":
                    request.session['id'] = check.id
                    request.session['loggeduser'] = check.name
                    request.session['loginid'] = loginid
                    request.session['email'] = check.email
                    return render(request, 'users/UserHomePage.html')
                else:
                    messages.error(request, 'Your account is not activated.')
            else:
                messages.error(request, 'Invalid password.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid login ID.')
    return render(request, 'UserLogin.html')

# ================================
# User Home
# ================================
def UserHome(request):
    return render(request, 'users/UserHomePage.html')

# ================================
# Dataset Viewer
# ================================
def DatasetView(request):
    dataset_path = os.path.join(settings.MEDIA_ROOT, "heart_disease_dataset_30000_rows.csv")
    try:
        df = pd.read_csv(dataset_path)
        df.columns = df.columns.str.strip().str.lower()
        df_html = df.head(100).to_html(classes='table table-striped')
        return render(request, 'users/viewdataset.html', {'data': df_html})
    except Exception as e:
        return render(request, 'users/viewdataset.html', {'data': f"<p>Error loading dataset: {str(e)}</p>"})

# ================================
# Model Training
# ================================
def training(request):
    dataset_path = os.path.join(settings.MEDIA_ROOT, "heart_disease_dataset_30000_rows.csv")
    data = pd.read_csv(dataset_path)

    features = data[['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal']]
    labels = data['target']

    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=80, max_depth=6, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6),
        "KNN": KNeighborsClassifier(n_neighbors=15)
    }

    accuracy_results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        accuracy_results.append((name, round(acc*100,2)))

    # Accuracy Table
    accuracy_table = "<table class='table table-bordered'><tr><th>Model</th><th>Accuracy (%)</th></tr>"
    for name, score in accuracy_results:
        accuracy_table += f"<tr><td>{name}</td><td>{score}</td></tr>"
    accuracy_table += "</table>"

    # Plot 1: Accuracy Comparison
    names = [x[0] for x in accuracy_results]
    scores = [x[1] for x in accuracy_results]
    plt.figure()
    plt.bar(names, scores)
    plt.xlabel("Machine Learning Algorithms")
    plt.ylabel("Accuracy (%)")
    plt.title("Accuracy Comparison")
    plt.savefig(os.path.join(settings.MEDIA_ROOT, "accuracy_graph.png"))
    plt.close()

    # Plot 2: Target Distribution
    plt.figure()
    data['target'].value_counts().plot(kind='bar')
    plt.xlabel("Heart Disease")
    plt.ylabel("Count")
    plt.title("Heart Disease Distribution")
    plt.savefig(os.path.join(settings.MEDIA_ROOT, "target_distribution.png"))
    plt.close()

    # Plot 3: Age vs Heart Disease
    plt.figure()
    plt.scatter(data['age'], data['target'])
    plt.xlabel("Age")
    plt.ylabel("Heart Disease")
    plt.title("Age vs Heart Disease")
    plt.savefig(os.path.join(settings.MEDIA_ROOT, "age_vs_disease.png"))
    plt.close()

    return render(request, 'users/training.html', {
        'accuracy_table': accuracy_table,
        'plot1': "/media/accuracy_graph.png",
        'plot2': "/media/target_distribution.png",
        'plot3': "/media/age_vs_disease.png"
    })

# ================================
# Prediction with Dropdowns
# ================================
def prediction(request):
    dataset_path = os.path.join(settings.MEDIA_ROOT, "heart_disease_dataset_30000_rows.csv")
    data = pd.read_csv(dataset_path)

    features = data[['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal']]
    labels = data['target']

    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    prediction_result = None

    if request.method == 'POST':
        user_input = pd.DataFrame([{
            'age': int(request.POST.get('age')),
            'sex': int(request.POST.get('sex')),
            'cp': int(request.POST.get('cp')),
            'trestbps': int(request.POST.get('trestbps')),
            'chol': int(request.POST.get('chol')),
            'fbs': int(request.POST.get('fbs')),
            'restecg': int(request.POST.get('restecg')),
            'thalach': int(request.POST.get('thalach')),
            'exang': int(request.POST.get('exang')),
            'oldpeak': float(request.POST.get('oldpeak')),
            'slope': int(request.POST.get('slope')),
            'ca': int(request.POST.get('ca')),
            'thal': int(request.POST.get('thal'))
        }])

        result = model.predict(user_input)[0]
        prediction_result = "Cardiovascular Disease Detected" if result==1 else "Healthy"

    context = {
        'prediction': prediction_result,
        'cp_choices': CP_CHOICES,
        'restecg_choices': RESTECG_CHOICES,
        'slope_choices': SLOPE_CHOICES,
        'thal_choices': THAL_CHOICES
    }

    return render(request, 'users/predict.html', context)