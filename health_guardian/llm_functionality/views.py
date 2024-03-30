import markdown2
import google.generativeai as genai
from django.shortcuts import render
from django.utils.safestring import mark_safe
from health_guardian.settings import GOOGLE_API_KEY
from Predict.views import predict_view
import textwrap

# Create your views here.

genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel('gemini-pro')


def generate_diet(request, disease):
    model = genai.GenerativeModel('gemini-pro')
    # Generate content using the model
    response = model.generate_content(f"generate a diet chart for a person having {disease} disease")
    
    # Convert generated text to Markdown
    # Convert Markdown to HTML
    html_content = markdown2.markdown(response.text)
    
    # Pass the generated content to the template
    return render(request, 'diet.html', {'content': html_content})


def generate_precaution(request, disease):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    # Generate content using the model
    response = model.generate_content(f"generate a precautions for a person having {disease} disease")
    
    # Convert generated text to Markdown
    # Convert Markdown to HTML
    html_content = markdown2.markdown(response.text)
    
    # Pass the generated content to the template
    return render(request, 'precaution.html', {'content': html_content})

    
  
