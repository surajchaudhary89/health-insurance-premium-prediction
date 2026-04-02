import streamlit as st
import pandas as pd
import joblib

st.set_page_config(
    page_title="InsurancePremium Predictor",
    page_icon="🏥",
    layout="centered"
)

# customer CSS styling for better UI
st.markdown("""
    <style>
        .header {
            font-size: 38px;
            text-align: center;
            font-weight: bold;
            color: #DF8B7C
        }
        .sub-text {
            text-align: left;
            font-size: 16px;
            color: #F5F1F0;
            margin-bottom: 30px;
        }
        .result-card {
            background-color: #e8f5e9;
            padding: 25px;
            border-radius: 18px;
            text-align: center;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .premium-text {
            font-size: 18px;
            color: #444;
        }
        .premium-value {
            font-size: 34px;
            font-weight: bold;
            color: #1b5e20;
        }
        .section-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #1f4e79;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🏥Health Insurance Premium Predictor</div><br>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-top: -10px; margin-bottom: 25px;'>
    <h4 style='color: #F5F1F0; font-weight: 500;'>
        Predict your annual health insurance premium in seconds
    </h4>
    <p style='font-size: 16px; color: #F5F1F0; margin-top: -8px;'>
        Powered by your health profile, lifestyle habits, and family risk factors.
    </p>
</div>
""", unsafe_allow_html=True)

#loading models using joblib
model_young = joblib.load("artifacts/model_young.pkl")
model_old = joblib.load("artifacts/model_old.pkl")

# defining function for breakdown of premium
def get_premium_breakdown(age, smoking_status, insurance_plan, genetical_risk, bmi_category, medical_history):
    breakdown = {
        "Smoking Impact": 0,
        "Insurance Plan Impact": 0,
        "Genetical Risk Impact": 0,
        "BMI Impact": 0,
        "Medical History Impact": 0
    }

    # Smoking
    if smoking_status == "Regular":
        breakdown["Smoking Impact"] = 1200
    elif smoking_status == "Occasional":
        breakdown["Smoking Impact"] = 800

    # Insurance Plan
    if insurance_plan == "Silver":
        breakdown["Insurance Plan Impact"] = 1800
    elif insurance_plan == "Gold":
        breakdown["Insurance Plan Impact"] = 4000

    # Genetical Risk
    list_of_risks = genetical_risk if isinstance(genetical_risk, list) else []
    if "No Family History" in list_of_risks or len(list_of_risks) == 0:
        breakdown["Genetical Risk Impact"] = 0
    elif any(risk in list_of_risks for risk in ["Heart Disease", "Thyroid", "Asthma", "Cancer"]):
        breakdown["Genetical Risk Impact"] = 2000
    elif any(risk in list_of_risks for risk in ["Diabetes", "High Blood Pressure", "Obesity"]):
        breakdown["Genetical Risk Impact"] = 1000
    
    # # Genetical Risk
    # if genetical_risk == "No Family History" or len(genetical_risk) == 0:
    #     breakdown["Genetical Risk Impact"] = 0
    # elif genetical_risk == "Diabetes" or genetical_risk == "High Blood Pressure"  or genetical_risk == "Obesity":
    #     breakdown["Genetical Risk Impact"] = 1000
    # elif genetical_risk == "Heart Disease" or genetical_risk == "Thyroid" or genetical_risk == "Asthma" or genetical_risk == "Cancer":
    #     breakdown["Genetical Risk Impact"] = 2000

    # BMI
    if bmi_category == "Overweight":
        breakdown["BMI Impact"] = 1000
    elif bmi_category == "Obesity":
        breakdown["BMI Impact"] = 2500
    elif bmi_category == "Underweight":
        breakdown["BMI Impact"] = 800

    # Medical history
    if medical_history == "No Disease":
        breakdown["Medical History Impact"] = 0
    elif "&" in medical_history:
        breakdown["Medical History Impact"] = 3500
    else:
        breakdown["Medical History Impact"] = 1800

    return breakdown

# calculating genetical risk based on family history
def calculate_genetical_risk_score(family_history):
    if len(family_history) == 0:
        return 0
    
    risk_scores = {
        "Diabetes": 1,
        "High Blood Pressure": 1,
        "Heart Disease": 2,
        "Thyroid": 1,
        "Cancer": 3,
        "Asthma": 1,
        "Obesity": 1
    }

    total_score = sum(risk_scores.get(condition, 0) for condition in family_history)

    return min(total_score, 5)

# calculating risk score based on medical history
def calculate_risk_score(medical_history):

    disease_weights = {
    "diabetes": 6,
    "heart disease": 8,
    "high blood pressure": 6,
    "thyroid": 5,
    "no disease": 0,
    "none": 0
    }

    diseases = medical_history.split(" & ")
    risk_score = sum(disease_weights.get(disease.strip().lower(), 0) for disease in diseases)
    return risk_score

# input form

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=24)
    gender = st.selectbox("Gender", ["Male", "Female"])
    region = st.selectbox("Region", ["North", "East", "South", "West"])
    marital_status = st.selectbox("Marital Status", ["Unmarried", "Married"])
    number_of_dependants = st.number_input("Number Of Dependants", min_value=0, max_value=10, value=0)
    bmi_category = st.selectbox("BMI Category", ["Normal","Underweight", "Overweight", "Obesity"], help="Not sure? [Calculate your BMI here](https://www.calculator.net/bmi-calculator.html).")

with col2:
    smoking_status = st.selectbox("Smoking Status", ["No Smoking", "Regular", "Occasional"])
    employment_status = st.selectbox("Employment Status", ["Salaried", "Self-Employed", "Freelancer"])
    income_lakhs = st.number_input("Income (in Lakhs)", min_value=0.0, max_value=100.0, value=5.0, step=0.25)
    medical_history = st.selectbox(
        "Medical History",
        [
            "No Disease",
            "Diabetes",
            "High blood pressure",
            "Thyroid",
            "Heart disease",
            "Diabetes & High blood pressure",
            "Diabetes & Thyroid",
            "High blood pressure & Heart disease",
            "Diabetes & Heart disease"
        ]
    )
    insurance_plan = st.selectbox("Insurance Plan", ["Bronze", "Silver", "Gold"])
    genetical_risk = st.multiselect(
    "Family Medical History (if any)",
    [
        "Diabetes",
        "High Blood Pressure",
        "Heart Disease",
        "Thyroid",
        "Cancer",
        "Asthma",
        "Obesity"
    ])


st.markdown('</div>', unsafe_allow_html=True)

# predict button
predict_clicked = st.button("Predict Premium", use_container_width=True)

# prediction logic
if predict_clicked:
    input_data = pd.DataFrame([{
        'age': age,
        'gender': gender,
        'region': region,
        'marital_status': marital_status,
        'number_of_dependants': number_of_dependants,
        'bmi_category': bmi_category,
        'smoking_status': smoking_status,
        'employment_status': employment_status,
        'income_lakhs': income_lakhs,
        'medical_history': medical_history,
        'insurance_plan': insurance_plan,
        'family_history_given': genetical_risk
    }])

    input_data['genetical_risk'] = input_data['family_history_given'].apply(calculate_genetical_risk_score)
    input_data['medical_risk_score'] = input_data['medical_history'].apply(calculate_risk_score)
    input_data['genetical_risk'] = [0 if age > 25 else score for score in input_data['genetical_risk']]
    
    input_data.drop(columns=['family_history_given', 'medical_history'], inplace=True)


    if age < 26:
        prediction = model_young.predict(input_data)[0]
        age_group = "Age (< 26)"
    else:
        prediction = model_old.predict(input_data)[0]
        age_group = "Age (>= 26)"

    prediction = round(prediction, 2)

    # breakdown
    breakdown = get_premium_breakdown(
        age, smoking_status, insurance_plan, genetical_risk, bmi_category, medical_history
    )

    # custom desiged result card
    st.markdown(f"""
        <div class="result-card">
            <div class="premium-text">Predicted Annual Premium</div>
            <div class="premium-value">₹ {prediction:,.2f}</div>
            <div class="premium-text">Model Used: <b>{age_group}</b></div>
        </div>
    """, unsafe_allow_html=True)

    # detailed breakdown and customer summary
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 📊 Estimated Premium Drivers")
        for k, v in breakdown.items():
            st.write(f"**{k}:** ₹ {v:,.0f}")

    with col4:
        st.markdown("#### 🧾 Customer Summary")
        st.write(f"**Plan:** {insurance_plan}")
        st.write(f"**Smoking:** {smoking_status}")
        st.write(f"**BMI:** {bmi_category}")
        st.write(f"**Medical History:** {medical_history}")
        st.write(f"**Genetical Risk:** {genetical_risk}")