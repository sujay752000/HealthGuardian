import markdown2
import google.generativeai as genai
from django.shortcuts import render
from django.utils.safestring import mark_safe
from health_guardian.settings import GOOGLE_API_KEY
from Predict.views import predict_view
import textwrap
from django.http import JsonResponse

# Create your views here.

genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel('gemini-pro')

def generateHealthTip():
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Generate a concise health tip for the day, aimed at promoting wellness and healthy habits. Your tip should be informative, actionable, and achievable within a day, all within 50 words. Consider aspects like nutrition, exercise, mental health, sleep hygiene, or general well-being to offer a holistic approach to daily health.")
    return response.text

def generateAboutDisease(disease):
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(f"Compose a concise description of a {disease} with in 30 words. Include information about its symptoms, causes, and possible treatments. Make sure to emphasize the significance of the disease and its impact on individuals or society. Consider using medical terminology to convey accuracy and clarity. Your description should provide enough detail to educate readers about the disease while maintaining brevity and readability.")
        return response.text
    except:
        return None




def generate_diet(disease, chronic_disease, bmi):
    model = genai.GenerativeModel('gemini-pro')
    # Generate content using the model
    response = model.generate_content(f"Generate a comprehensive dietary regimen for an individual grappling with {disease}, considering any chronic conditions {chronic_disease} and their Body Mass Index {bmi}. The plan should encompass the total number of daily meals, their corresponding calorie values, and specify the recommended water intake. Additionally, incorporate essential minerals and vitamins tailored to manage the symptoms of the specified disease and support overall health. Factor in the individual's BMI and any coexisting chronic illnesses to ensure the plan is both effective and safe.")
    
    # Convert generated text to Markdown
    # Convert Markdown to HTML
    html_content = markdown2.markdown(response.text)

    return html_content


def generate_precaution(disease, chronic_disease, bmi):
    model = genai.GenerativeModel('gemini-pro')
    # Generate content using the model
    response = model.generate_content(f"Formulate a set of precautionary measures tailored for individuals vulnerable to {disease}, considering their BMI {bmi} and any pre-existing chronic conditions {chronic_disease}. Outline preventive actions encompassing lifestyle adjustments, exercise routines, and hygiene practices aimed at minimizing the risk of contracting or exacerbating the specified disease. Incorporate guidelines for managing stress levels and maintaining a healthy immune system. Additionally, provide information on regular screenings, vaccinations, and consultations with healthcare professionals to monitor and address any emerging health concerns effectively.")
    
    # Convert generated text to Markdown
    # Convert Markdown to HTML
    html_content = markdown2.markdown(response.text)

    return html_content


def chatAssistantResponse(request):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"{request.GET.get('prompt')}")
    return JsonResponse({'message': response.text.replace("*", "")})



def generate_diet_doctor(disease):
    model = genai.GenerativeModel('gemini-pro')
    # Generate content using the model

    response = model.generate_content(f"Develop a comprehensive dietary regimen for an individual grappling with {disease}, emphasizing nutrition tailored to manage symptoms and promote overall health. Consider the total number of daily meals, their corresponding calorie values, and specify the recommended water intake. Additionally, incorporate essential minerals and vitamins suited to support the individual's nutritional needs. Ensure the plan is both effective and safe by accounting for any dietary restrictions or preferences.")
    
    # Convert generated text to Markdown
    # Convert Markdown to HTML
    html_content = markdown2.markdown(response.text)

    return html_content



def generate_precaution_doctor(disease):
    model = genai.GenerativeModel('gemini-pro')
    # Generate content using the model

    response = model.generate_content(f"Develop a set of precautionary measures tailored for individuals vulnerable to {disease}, focusing on lifestyle adjustments, exercise routines, and hygiene practices to minimize the risk of contracting or exacerbating the specified disease. Outline preventive actions aimed at maintaining overall health and reducing exposure to potential health risks. Incorporate guidelines for managing stress levels and boosting immune function. Additionally, provide information on regular screenings, vaccinations, and consultations with healthcare professionals to monitor and address any emerging health concerns effectively.")
    
    # Convert generated text to Markdown
    # Convert Markdown to HTML
    html_content = markdown2.markdown(response.text)

    return html_content


