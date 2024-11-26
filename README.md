### Project deployed at https://getufit-58742455872.us-central1.run.app

# GetUFit - Personalized Health and Fitness Chatbot

**Project deployed at:** [GetUFit](https://getufit-58742455872.us-central1.run.app)

## Project Overview

GetUFit is a personalized health and fitness chatbot that combines Generative AI and Retrieval-Augmented Generation (RAG) with advanced AI models to deliver tailored fitness and wellness assistance. This project leverages **Google Cloud Platform (GCP)** and **Vertex AI** to streamline data integration and enhance user experience.

### Key Features:
1. **Demographic Information Collection**: Captures user details such as age, gender, weight, and goals to create personalized recommendations.
2. **Activity Generation Based on User Data**: Suggests tailored fitness activities, routines, and nutritional plans using AI-powered models like Gemini 1.5 Pro.
3. **Fitness Bot**: Provides real-time assistance with fitness queries.
4. **Personalized RAG Model**: Combines user data with relevant external knowledge using Text Embedding Gecko and Gemini Flash for precise responses.
5. **File Download Capability**: Users can download chat history and wellness plans in PDF format.

---

## Target Audience

GetUFit caters to a diverse audience, including:
- **Fitness Enthusiasts**: Personalized plans for achieving fitness goals.
- **Beginners**: Guidance for starting a fitness journey.
- **Health-Conscious Individuals**: Balanced wellness advice.
- **Busy Professionals**: Time-efficient workouts and plans.
- **Individuals with Specific Goals**: Weight loss, muscle gain, event training, etc.
- **People with Chronic Health Conditions**: Safe, condition-specific exercises.
- **Students and Young Adults**: Affordable, easy-to-follow recommendations.
- **Organizations and Communities**: Tailored solutions for gyms, schools, and workplaces.

---

## Architecture Overview

The architecture leverages the following GCP services:
- **Google Firestore**: To store user profiles and chat data.
- **BigQuery**: For analyzing and retrieving user-specific health insights.
- **Vertex AI**: For embedding generation and AI-powered fitness recommendations.
- **Google Cloud Storage (GCS)**: For storing downloadable files like PDFs.

### Workflow:
1. Users input their demographic details and fitness queries.
2. Data is processed and stored in BigQuery for structured insights.
3. Fitness activities and recommendations are generated using Gemini 1.5 Pro.
4. The RAG model retrieves user-specific records and provides responses using Text Embedding Gecko and Gemini Flash.
5. Users can download personalized plans and chat history.
![user details](https://github.com/user-attachments/assets/6cf94bc6-15ab-4e0c-a746-ed57bd2f3ec9)

   

---

## Project Setup

This repository contains the following components:
- **Backend (Flask Application)**
- **Dataflow (Firestore to BigQuery Integration)**
- **Frontend (GetUFitV1 - Next.js)**
- **RAG Model (Flask Application)**

---

### 1. Backend (Flask Application)

The backend is built using Flask and serves as the core API layer.

**Steps to Setup:**
1. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Place your `service.json` file in the same directory as the `app.py` file.
4. Run the application:
    ```bash
    python app.py
    ```

---

### 2. Dataflow (Firestore to BigQuery Integration)

**Steps to Setup:**
1. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Place your `service.json` file in the same directory as the `app.py` file.
4. Run the application:
    ```bash
    python app.py
    ```

---

### 3. Frontend (GetUFitV1 - Next.js)

The frontend is built using Next.js and React for a user-friendly experience.

**Steps to Setup:**
1. Clone the repository:
    ```bash
    git clone https://github.com/raghavendra-10/getufit.git
    cd getufit
    ```
2. Install the dependencies:
    ```bash
    npm install
    ```
3. Run the application:
    ```bash
    npm run dev
    ```

---

### 4. RAG Model (Flask Application)

The RAG model backend is built using Flask and combines AI-based retrieval and generative capabilities.

**Steps to Setup:**
1. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Place your `service.json` file in the same directory as the `app.py` file.
4. Run the application:
    ```bash
    python app.py
    ```



---

## Acknowledgments

I would like to thank my mentor **Mr. Mahesh Mohan** (boggavarapumohanmahesh@gmail.com) for guiding me in building this project end-to-end.

To learn more about Google Cloud Services and create an impact with your work:
- Register for **Code Vipassana** sessions.
- Join the **Datapreneur Social** meetup group.
- Sign up to become a **Google Cloud Innovator**.

---


# Project Setup

This repository contains the following components:

1. **Backend (Flask Application)**
2. **Dataflow (Firestore to BigQuery Integration)**
3. **Frontend (GetuFitV1 - Next.js)**
4. **RAG Model**

---

## 1. Backend (Flask Application)

The backend is built using Flask and serves as the core API layer. It requires the following setup:

### Steps to Setup:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
3. Place your service.json file in the same directory as the app.py file.
4. run the appilication
   ```bash
   python app.py


## 2. Dataflow 
### Steps to Setup:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
3. Place your service.json file in the same directory as the app.py file.
4. run the appilication
   ```bash
   python app.py

## 3. Frontend
1. Download packages:
   ```bash
   npm install

2. run the appilication
   ```bash
   npm run dev

## 4. Rag model (Flask Application)

The backend is built using Flask and serves as the core API layer. It requires the following setup:

### Steps to Setup:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
3. Place your service.json file in the same directory as the app.py file.
4. run the appilication
   ```bash
   python app.py


## Output

![Screenshot 2024-11-26 075025](https://github.com/user-attachments/assets/fb574d6a-059d-4412-933e-bff64fc8a6cb)
![Screenshot 2024-11-26 075140](https://github.com/user-attachments/assets/3dd27ac4-9771-4879-baf2-27b432bf88b4)
![Screenshot 2024-11-26 075153](https://github.com/user-attachments/assets/f6473254-87a6-4490-a661-91a0944b4b22)
![Screenshot 2024-11-26 075214](https://github.com/user-attachments/assets/b46ec7e5-df74-4489-a58f-a53ec5afa360)
![Screenshot 2024-11-26 075228](https://github.com/user-attachments/assets/49edb42e-584f-4776-b6d5-b2263cd84783)
![Screenshot 2024-11-26 075248](https://github.com/user-attachments/assets/f5170687-3982-4eb7-b407-53eb0af5124f)



