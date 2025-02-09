HealthGuardian

HealthGuardian is a smart web application that leverages machine learning algorithms to predict diseases based on user symptoms. It offers seamless doctor appointments, video consultations, real-time chats, and AI-powered insights powered by LLM (Gemini). The platform enhances healthcare accessibility and enables proactive health management.

Features

Disease Prediction: Uses ML models like Naive Bayes, Random Forest, and SVM for accurate diagnosis.

Doctor Appointments: Schedule and manage medical appointments with ease.

Video Consultations: Connect with healthcare professionals via video calls.

Real-time Chat: Engage in live chats with doctors for instant medical advice.

AI-Powered Insights: Get personalized precautions and diet plans with LLM (Gemini).

Health Chatbot: AI-powered chatbot for health-related queries and assistance.

Tech Stack

Backend: Python, Django, Django Channels, Daphne

Frontend: HTML, CSS, JavaScript

Database: SQLite, Redis DB

WebSockets: Channels and Daphne for real-time communication

ML Models: Naive Bayes, Random Forest, SVM

AI Integration: Google Gemini API for LLM-based insights

Installation

Prerequisites

Python 3.11.2

Virtual Environment (optional but recommended)

Redis (for WebSocket support)

Setup

Clone the repository

git clone "https://github.com/sujay752000/HealthGuardian.git"
cd HealthGuardian

Create and activate a virtual environment

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows

Install dependencies

pip install -r requirements.txt

Set up environment variables
Create a .env file in the root directory and add necessary configurations like database credentials and API keys.

Run database migrations

python manage.py migrate

Start the development server

python manage.py runserver

Deployment

For production deployment:

Use Gunicorn and Daphne for ASGI support.

Configure NGINX and Redis for handling WebSockets.

Deploy on AWS EC2, DigitalOcean, or any cloud provider.

Contributing

Contributions are welcome! Feel free to fork the repo, create a new branch, and submit a pull request.

License

This project is licensed under the MIT License.
