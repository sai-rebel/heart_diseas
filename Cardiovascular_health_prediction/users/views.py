from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import UserRegistrationModel
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

# ================================
# User Registration View
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
# User Login View
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
# Index Page
# ================================
def index(request):
    return render(request, "index.html")


# ================================
# Dataset Viewer
# ================================
def DatasetView(request):
    try:
        df = pd.read_csv(r"C:\Users\datapoint\Documents\Prediction of Cardiovascular Health Status Using Machine Learning Algorithms\Cardiovascular_health_prediction\media\Cardio_balanced_dataset.csv")
        df.columns = df.columns.str.strip().str.lower()
        df_html = df.head(100).to_html(classes='table table-striped')
        return render(request, 'users/viewdataset.html', {'data': df_html})
    except Exception as e:
        return render(request, 'users/viewdataset.html', {'data': f"<p>Error loading dataset: {str(e)}</p>"})


# ================================
# Model Training
# ================================
def training(request):
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    import numpy as np
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    from tabulate import tabulate
    import os
    from django.conf import settings

    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score

    # Veri setini oku
    data = pd.read_csv(r'C:\Users\datapoint\Documents\Prediction of Cardiovascular Health Status Using Machine Learning Algorithms\Cardiovascular_health_prediction\media\Cardio_balanced_dataset.csv')

    # Başlık ve özet tabloları
    head_data = data.head().to_html(classes="table table-striped")
    summary = data.describe().to_html(classes="table table-bordered")

    numerical_vars = ['id', 'age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active', 'cardio']
    for var in numerical_vars:
        print(f"{data[var].value_counts()}")

    # 1. Sadece 1 ve 2 olan gender değerlerini al
    data = data[data['gender'].isin([1, 2])]

    # 2. Sayısal değerleri string olarak etiketle
    data['gender'] = data['gender'].map({1: 'Women', 2: 'Men'})

    # Yaşı yıl cinsine dönüştür
    data['age_years'] = (data['age'] / 365).astype(int)

    # Grafiklerin kaydedileceği klasör
    plot_dir = os.path.join(settings.MEDIA_ROOT, 'plots')
    os.makedirs(plot_dir, exist_ok=True)
    plot_paths = []

    # Grafik kaydetme yardımcı fonksiyonu
    def save_plot(fig, name):
        path = os.path.join(plot_dir, name)
        fig.savefig(path)
        plot_paths.append(os.path.join('media/plots', name))
        plt.close(fig)

    # Gender grafiği
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='gender', palette=sns.color_palette("flare", n_colors=2))
    plt.title('Gender Distribution')
    save_plot(fig, 'gender.png')

    # Yaş grafiği
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='age_years', palette=sns.color_palette("flare"))
    plt.title('Age Distribution')
    plt.xticks(rotation=45)
    save_plot(fig, 'age.png')

    # Weight group grafiği
    bins = [-np.inf, 40, 50, 60, 70, 80, 90, 100, 120, np.inf]
    labels = ['<40', '40–50', '50–60', '60–70', '70–80', '80–90', '90–100', '100–120', 'Outlier']
    data['weight_group'] = pd.cut(data['weight'], bins=bins, labels=labels)
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='weight_group', palette=sns.color_palette("flare", n_colors=len(labels)))
    plt.title("Weight Distribution")
    plt.xticks(rotation=45)
    save_plot(fig, 'weight.png')

    # Height group grafiği
    bins = [-np.inf, 140, 150, 160, 165, 170, 175, 185, np.inf]
    labels = ['<140', '140–150', '150–160', '160–165', '165–170', '170–175', '175–185', 'Outlier']
    data['height_group'] = pd.cut(data['height'], bins=bins, labels=labels)
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='height_group', palette=sns.color_palette("flare", n_colors=len(labels)))
    plt.title("Height Distribution")
    plt.xticks(rotation=45)
    save_plot(fig, 'height.png')

    # Systolic BP
    ap_hi_bins = [-np.inf, 90, 110, 130, 150, 180, 300, np.inf]
    ap_hi_labels = ['<90', '90–110', '110–130', '130–150', '150–180', '180–300', 'Outlier']
    data['ap_hi_group'] = pd.cut(data['ap_hi'], bins=ap_hi_bins, labels=ap_hi_labels)
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='ap_hi_group', palette=sns.color_palette("flare", n_colors=len(ap_hi_labels)))
    plt.title("Systolic Blood Pressure Distribution")
    plt.xticks(rotation=45)
    save_plot(fig, 'ap_hi.png')

    # Diastolic BP
    ap_lo_bins = [-np.inf, 60, 70, 80, 90, 100, 130, np.inf]
    ap_lo_labels = ['<60', '60–70', '70–80', '80–90', '90–100', '100–130', 'Outlier']
    data['ap_lo_group'] = pd.cut(data['ap_lo'], bins=ap_lo_bins, labels=ap_lo_labels)
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='ap_lo_group', palette=sns.color_palette("flare", n_colors=len(ap_lo_labels)))
    plt.title("Diastolic Blood Pressure Distribution")
    plt.xticks(rotation=45)
    save_plot(fig, 'ap_lo.png')

    # Cholesterol
    data['chol_group'] = data['cholesterol'].map({1: 'Normal', 2: 'Above Normal', 3: 'Well Above Normal'})
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='chol_group', palette='flare')
    plt.title("Cholesterol Distribution")
    save_plot(fig, 'cholesterol.png')

    # Glucose
    data['gluc_group'] = data['gluc'].map({1: 'Normal', 2: 'Above Normal', 3: 'Well Above Normal'})
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='gluc_group', palette='flare')
    plt.title("Glucose Distribution")
    save_plot(fig, 'glucose.png')

    # Smoking
    data['smoke_group'] = data['smoke'].map({0: 'Non-Smoker', 1: 'Smoker'})
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='smoke_group', palette='flare')
    plt.title("Smoking Status Distribution")
    save_plot(fig, 'smoke.png')

    # Alcohol
    data['alcohol_group'] = data['alco'].map({0: 'Non-Drinker', 1: 'Drinks Alcohol'})
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='alcohol_group', palette='flare')
    plt.title("Alcohol Status Distribution")
    save_plot(fig, 'alcohol.png')

    # Physical Activity
    data['active_group'] = data['active'].map({0: 'Inactive', 1: 'Physically Active'})
    fig = plt.figure(figsize=(8, 6))
    sns.countplot(data=data, x='active_group', palette='flare')
    plt.title("Physical Activity Distribution")
    save_plot(fig, 'activity.png')

    # Korelasyon matrisi
    fig = plt.figure(figsize=(8, 6))
    numeric_data = data.select_dtypes(include=['number'])
    sns.heatmap(numeric_data.corr(), annot=True, cmap='flare', fmt='.2f')
    plt.title("Correlation Matrix")
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    save_plot(fig, 'correlation_matrix.png')

    # === MACHINE LEARNING MODELS ===
    features = data.drop(columns=['id', 'cardio', 'gender', 'chol_group', 'gluc_group',
                                   'smoke_group', 'alcohol_group', 'active_group',
                                   'weight_group', 'height_group', 'ap_hi_group', 'ap_lo_group'])
    labels = data['cardio']

    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(),
        "Decision Tree": DecisionTreeClassifier(),
        "KNN": KNeighborsClassifier()
    }

    accuracy_results = []

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        accuracy_results.append((model_name, round(acc * 100, 2)))

    # Accuracy table HTML
    accuracy_table = "<table class='table table-bordered'><thead><tr><th>Model</th><th>Accuracy (%)</th></tr></thead><tbody>"
    for name, score in accuracy_results:
        accuracy_table += f"<tr><td>{name}</td><td>{score}</td></tr>"
    accuracy_table += "</tbody></table>"

    context = {
        'head_data': head_data,
        'summary': summary,
        'plot_paths': plot_paths,
        'accuracy_table': accuracy_table
    }

    return render(request, 'users/training.html', context)




# ================================
# Prediction View
# ================================
def prediction(request):
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    # Load and preprocess dataset
    data = pd.read_csv(r'C:\Users\datapoint\Documents\Prediction of Cardiovascular Health Status Using Machine Learning Algorithms\Cardiovascular_health_prediction\media\Cardio_balanced_dataset.csv')

    # Keep valid genders only
    data = data[data['gender'].isin([1, 2])]

    # Create 'age_years' column for consistency
    data['age_years'] = (data['age'] / 365).astype(int)

    # Select same features for training and prediction
    features = data[['age', 'age_years', 'height', 'weight', 'ap_hi', 'ap_lo']]
    labels = data['cardio']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)

    # Train model (Logistic Regression used here)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    prediction = None

    if request.method == 'POST':
        # Get values from form
        age = int(request.POST.get('age'))
        height = float(request.POST.get('height'))
        weight = float(request.POST.get('weight'))
        ap_hi = int(request.POST.get('ap_hi'))
        ap_lo = int(request.POST.get('ap_lo'))

        # Create input with exact same features used during training
        user_input = pd.DataFrame([{
            'age': age * 365,         # for 'age' in training
            'age_years': age,         # for 'age_years' in training
            'height': height,
            'weight': weight,
            'ap_hi': ap_hi,
            'ap_lo': ap_lo
        }])

        result = model.predict(user_input)[0]
        prediction = "✅ Cardiovascular Disease Detected" if result == 1 else "🟢 healthy "

    return render(request, 'users/predict.html', {'prediction': prediction})



