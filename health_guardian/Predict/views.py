from django.shortcuts import render, redirect
from django.contrib import messages
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd
import warnings
import statistics
from joblib import load


# Create your views here.

# Load pre-trained models
final_svm_model = load('D:/Final_Year_Project/health_guardian/Savedmodels/final_svm_model.joblib')
final_nb_model = load('D:/Final_Year_Project/health_guardian/Savedmodels/final_nb_model.joblib')
final_rf_model = load('D:/Final_Year_Project/health_guardian/Savedmodels/final_rf_model.joblib')

# Load pre-trained LabelEncoder
encoder = load('D:/Final_Year_Project/health_guardian/Savedmodels/encoder.joblib')

test_data = pd.read_csv("D:/Final_Year_Project/health_guardian/dataset/Testing.csv").dropna(axis=1)
true_labels = test_data["prognosis"].tolist()

X = test_data.iloc[:,:-1]

symptoms = X.columns.values
 
# Creating a symptom index dictionary to encode the
# input symptoms into numerical form
symptom_index = {}
for index, value in enumerate(symptoms):
    symptom = " ".join([i.capitalize() for i in value.split("_")])
    symptom_index[symptom] = index


# # Gives the Symptoms names
# print(symptom_index.keys())    


 
data_dict = {
    "symptom_index":symptom_index,
    "predictions_classes":encoder.classes_
}
 
# Defining the Function
# Input: string containing symptoms separated by commas
# Output: Generated predictions by models
def calculate_accuracy(true_labels, predicted_labels):
    return accuracy_score(true_labels, predicted_labels)


def predictDisease(symptoms):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        
        symptoms = symptoms.split(",")
        
        # creating input data for the models
        input_data = [0] * len(data_dict["symptom_index"])
        for symptom in symptoms:
            index = data_dict["symptom_index"][symptom]
            input_data[index] = 1
            
        # reshaping the input data and converting it
        # into suitable format for model predictions
        input_data = np.array(input_data).reshape(1, -1)
        
        # generating individual outputs
        rf_prediction = data_dict["predictions_classes"][final_rf_model.predict(input_data)[0]]
        nb_prediction = data_dict["predictions_classes"][final_nb_model.predict(input_data)[0]]
        svm_prediction = data_dict["predictions_classes"][final_svm_model.predict(input_data)[0]]
        
        # making final prediction by taking mode of all predictions
        final_prediction = statistics.mode([rf_prediction, nb_prediction, svm_prediction])
        
        predictions = {
            "rf_model_prediction": rf_prediction,
            "naive_bayes_prediction": nb_prediction,
            "svm_model_prediction": svm_prediction,
            "final_prediction": final_prediction
        }

    print(predictions)

    return predictions["final_prediction"]

# providing input symptoms


def predict_view(request):
    symptoms = ['Itching', 'Skin Rash', 'Nodal Skin Eruptions', 'Continuous Sneezing', 'Shivering', 'Chills', 'Joint Pain', 'Stomach Pain', 'Acidity', 'Ulcers On Tongue', 'Muscle Wasting', 'Vomiting', 'Burning Micturition', 'Fatigue', 'Weight Gain', 'Anxiety', 'Cold Hands And Feets', 'Mood Swings', 'Weight Loss', 'Restlessness', 'Lethargy', 'Patches In Throat', 'Irregular Sugar Level', 'Cough', 'High Fever', 'Sunken Eyes', 'Breathlessness', 'Sweating', 'Dehydration', 'Indigestion', 'Headache', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Loss Of Appetite', 'Pain Behind The Eyes', 'Back Pain', 'Constipation', 'Abdominal Pain', 'Diarrhoea', 'Mild Fever', 'Yellow Urine', 'Yellowing Of Eyes', 'Acute Liver Failure', 'Fluid Overload', 'Swelling Of Stomach', 'Swelled Lymph Nodes', 'Malaise', 'Blurred And Distorted Vision', 'Phlegm', 'Throat Irritation', 'Redness Of Eyes', 'Sinus Pressure', 'Runny Nose', 'Congestion', 'Chest Pain', 'Weakness In Limbs', 'Fast Heart Rate', 'Pain During Bowel Movements', 'Pain In Anal Region', 'Bloody Stool', 'Irritation In Anus', 'Neck Pain', 'Dizziness', 'Cramps', 'Bruising', 'Obesity', 'Swollen Legs', 'Swollen Blood Vessels', 'Puffy Face And Eyes', 'Enlarged Thyroid', 'Brittle Nails', 'Swollen Extremeties', 'Excessive Hunger', 'Extra Marital Contacts', 'Drying And Tingling Lips', 'Slurred Speech', 'Knee Pain', 'Hip Joint Pain', 'Muscle Weakness', 'Stiff Neck', 'Swelling Joints', 'Movement Stiffness', 'Spinning Movements', 'Loss Of Balance', 'Unsteadiness', 'Weakness Of One Body Side', 'Loss Of Smell', 'Bladder Discomfort', 'Foul Smell Of urine', 'Continuous Feel Of Urine', 'Passage Of Gases', 'Internal Itching', 'Toxic Look (typhos)', 'Depression', 'Irritability', 'Muscle Pain', 'Altered Sensorium', 'Red Spots Over Body', 'Belly Pain', 'Abnormal Menstruation',  'Watering From Eyes', 'Increased Appetite', 'Polyuria', 'Family History', 'Mucoid Sputum', 'Rusty Sputum', 'Lack Of Concentration', 'Visual Disturbances', 'Receiving Blood Transfusion', 'Receiving Unsterile Injections', 'Coma', 'Stomach Bleeding', 'Distention Of Abdomen', 'History Of Alcohol Consumption', 'Fluid Overload.1', 'Blood In Sputum', 'Prominent Veins On Calf', 'Palpitations', 'Painful Walking', 'Pus Filled Pimples', 'Blackheads', 'Scurring', 'Skin Peeling', 'Silver Like Dusting', 'Small Dents In Nails', 'Inflammatory Nails', 'Blister', 'Red Sore Around Nose', 'Yellow Crust Ooze']
    context_symptoms = {'my_list': symptoms}
    if request.method == 'POST':
        # Get the list of selected symptoms from the form
        user_symptoms = request.POST.getlist('native-select')

        if user_symptoms[0] == '':
            messages.error(request, "Please Enter your Symptoms")
            return redirect("predict")
        else:

            """ Calling the predicting disease function """
            predicted_disease = predictDisease(user_symptoms[0])

            final_prediction_accuracy = calculate_accuracy([true_labels[0]], [predicted_disease]) * 100

            # Pass the predicted disease to the template context
            context_symptoms = {
                'my_list': symptoms,
                'predicted_disease': predicted_disease,
                'final_prediction_accuracy': final_prediction_accuracy
            }
            # Pass the symptoms list to the template context

            return render(request, 'disease.html', context=context_symptoms)
            # return predicted_disease

    # If the request method is not POST, render the form again
    return render(request, 'disease.html', context=context_symptoms)


