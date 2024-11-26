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
- **Cloud Run**: For deploying the backend .

### Workflow:
1. Users input their demographic details and fitness queries.
2. Data is processed and stored in BigQuery for structured insights.
3. Fitness activities and recommendations are generated using Gemini 1.5 Pro.
4. The RAG model retrieves user-specific records and provides responses using Text Embedding Gecko and Gemini Flash.
5. Users can download personalized plans and chat history.
![user details](https://github.com/user-attachments/assets/6cf94bc6-15ab-4e0c-a746-ed57bd2f3ec9)

   

---

### 3. Frontend (GetUFitV1 - Next.js)

The frontend is built using Next.js, a powerful React framework for building fast, interactive web applications. This provides an intuitive interface for users to interact with the chatbot, input their health data, and access personalized fitness plans.

#### Key Features of the Frontend:
1. **User-Friendly Onboarding**:
   - Simple interface to collect user demographic details (name, age, weight, height, fitness goals, etc.).
   - Inputs are validated before being sent to the backend for processing.
2. **Real-Time Chat with the Fitness Bot**:
   - Chat with the bot to get personalized fitness and nutrition advice.
   - Frontend sends queries to the backend and displays AI-generated responses.
3. **Personalized Fitness Dashboard**:
   - Displays a summary of user data with tailored fitness insights.
   - Provides fitness plans and generated wellness recommendations.
4. **File Download Functionality**:
   - Allows users to download chat history and wellness plans as PDF files.
5. **Mobile-First Design**:
   - Optimized for both desktop and mobile devices to ensure a seamless experience.
  

## Acknowledgments

I would like to thank my mentor **Mr. Mahesh Mohan** (boggavarapumohanmahesh@gmail.com) for guiding me in building this project end-to-end.

To learn more about Google Cloud Services and create an impact with your work:
- Register for **Code Vipassana** sessions : https://rsvp.withgoogle.com/events/cv
- Join the **Datapreneur Social** meetup group. : https://www.meetup.com/datapreneur-social/
- Sign up to become a **Google Cloud Innovator**. : https://cloud.google.com/innovators

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

1. Backend code:
    ```python
      import os
      from flask import Flask, request, jsonify
      from google.cloud import firestore
      from google.oauth2 import service_account
      import vertexai
      from vertexai.generative_models import GenerativeModel
      from fpdf import FPDF
      from google.cloud import storage
      from datetime import datetime, timedelta
      import json
      from google.cloud import bigquery
      from flask_cors import CORS
      
      import logging
      logging.basicConfig(level=logging.DEBUG)
      
      # Path to the service account file
      SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "getufit.json")
      
      # Load service account credentials
      credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
      
      # Initialize Firestore client
      firestore_client = firestore.Client(credentials=credentials, project=credentials.project_id)
      storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
      bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
      # Initialize Flask app
      app = Flask(__name__)
      CORS(app)
      # Vertex AI configuration
      generation_config = {
          "max_output_tokens": 8192,
          "temperature": 1,
          "top_p": 0.95,
      }
      
      def call_gemini_api(query):
          """Call the Gemini model using Vertex AI."""
          # Initialize Vertex AI
          vertexai.init(project=credentials.project_id, location="us-central1", credentials=credentials)
      
          # Load the Gemini Pro model
          model = GenerativeModel("gemini-1.5-pro-002")
      
          
          base_prompt = (
              "You are a chatbot specialized in fitness, nutrition, and health wellness. "
              "You provide advice strictly related to fitness, nutrition, exercise routines, and wellness plans. "
              "Avoid any topics unrelated to fitness and health. "
              "If the user asks anything outside these topics, politely decline and redirect them to fitness-related inquiries.\n\n"
              "User query: {query}\n\n"
          )
      
      # Inject the user query into the base_prompt
          formatted_query = base_prompt.format(query=query)  # Ensure 'user_query' contains the actual user input
      
      # Generate response
          response = model.generate_content(
              [formatted_query], 
              generation_config=generation_config,
              stream=False,  # Disable streaming for simplicity
          )
      
          # Extract and return the generated content
          if hasattr(response, "text"):
              return response.text.strip()  # Return the text response
          else:
              return "Sorry, I could not generate a response."
          
      def gemini(query):
          """Call the Gemini model using Vertex AI."""
          # Initialize Vertex AI
          vertexai.init(project=credentials.project_id, location="us-central1", credentials=credentials)
      
          # Load the Gemini Pro model
          model = GenerativeModel("gemini-1.5-pro-002")
       
          # Generate response
          response = model.generate_content(
              [query],  # Pass the user query as a list of strings
              generation_config=generation_config,
              stream=False,  # Disable streaming for simplicity
          )
      
          # Extract and return the generated content
          if hasattr(response, "text"):
              return response.text.strip()  # Return the text response
          else:
              return "Sorry, I could not generate a response."
      
      
      @app.route("/onboard_user", methods=["POST"])
      def onboard_user():
          """Handle user onboarding and save data to Firestore and BigQuery."""
          try:
              # Collect user data from request
              user_data = request.json
              user_id = user_data.get("user_id")
      
              if not user_id:
                  return jsonify({"error": "user_id is required"}), 400
      
              # Validate required fields
              required_fields = ["name", "age", "height", "weight", "goal", "experience"]
              for field in required_fields:
                  if not user_data.get(field):
                      return jsonify({"error": f"{field} is required"}), 400
      
              # Save data to Firestore
              try:
                  logging.debug("Attempting to save user data to Firestore.")
                  firestore_client.collection("users").document(user_id).set(user_data)
                  logging.debug(f"Successfully saved user data to Firestore for user_id: {user_id}")
              except Exception as firestore_error:
                  logging.error(f"Error saving to Firestore: {firestore_error}")
      
              # Save data to BigQuery
              try:
                  logging.debug("Attempting to save user data to BigQuery.")
                  bigquery_table = "buildnblog.wellness_analytics.users"
                  row_to_insert = {
                      "user_id": user_id,
                      "name": user_data["name"],
                      "age": user_data["age"],
                      "height": user_data["height"],
                      "weight": user_data["weight"],
                      "goal": user_data["goal"],
                      "health_issues": user_data.get("health_issues", ""),
                      "experience": user_data["experience"],
                  }
                  bigquery_client.insert_rows_json(bigquery_table, [row_to_insert])
                  logging.debug(f"Successfully saved user data to BigQuery for user_id: {user_id}")
              except Exception as bigquery_error:
                  logging.error(f"Error saving to BigQuery: {bigquery_error}")
      
              # Return the saved data as the response
              return jsonify({
                  "message": "User onboarded successfully.",
                  "user_data": user_data
              })
      
          except Exception as e:
              logging.error(f"Error in /onboard_user: {e}")
              return jsonify({"error": str(e)}), 500
      
      @app.route("/chat", methods=["POST"])
      def chat():
          """Handle user queries and provide AI-generated responses."""
          try:
              # Get user input from request
              user_input = request.json.get("query")
              user_id = request.json.get("user_id")
      
              if not user_input or not user_id:
                  return jsonify({"error": "Invalid input"}), 400
      
              # Verify if user exists
              user_doc = firestore_client.collection("users").document(user_id).get()
              if not user_doc.exists:
                  return jsonify({"error": "User not found. Please create a user profile first."}), 404
      
              # Call the Gemini API
              response = call_gemini_api(user_input)
      
              # Save interaction to Firestore under the user's document
              chat_data = {
                  "query": user_input,
                  "response": response,
                  "timestamp": firestore.SERVER_TIMESTAMP
              }
              # Save chat data inside user's subcollection
              firestore_client.collection("users").document(user_id).collection("chats").add(chat_data)
      
              return jsonify({"response": response})
      
          except Exception as e:
              return jsonify({"error": str(e)}), 500
      
      @app.route("/generate_pdf", methods=["POST"])
      def generate_pdf():
          """Generate a PDF for a user's chat history and wellness plan."""
          try:
              # Get user_id from the request
              user_id = request.json.get("user_id")
              if not user_id:
                  return jsonify({"error": "user_id is required"}), 400
      
              # Fetch user profile
              user_doc = firestore_client.collection("users").document(user_id).get()
              if not user_doc.exists:
                  return jsonify({"error": "User not found"}), 404
              user_data = user_doc.to_dict()
      
              # Fetch chat history
              chats_ref = firestore_client.collection("users").document(user_id).collection("chats")
              chat_docs = chats_ref.stream()
              chat_history = [doc.to_dict() for doc in chat_docs]
      
              if not chat_history:
                  return jsonify({"error": "No chat history found for this user."}), 404
      
              # Create a PDF
              pdf = FPDF()
              pdf.add_page()
              pdf.set_font("Arial", size=12)
      
              # Add user profile to the PDF
              pdf.cell(200, 10, txt="Personalized Wellness Plan", ln=True, align="C")
              pdf.cell(200, 10, txt=f"User: {user_data.get('name', 'N/A')} (ID: {user_id})", ln=True)
              pdf.cell(200, 10, txt=f"Age: {user_data.get('age', 'N/A')} | Gender: {user_data.get('gender', 'N/A')}", ln=True)
              pdf.ln(10)  # Add some spacing
      
              # Add chat history to the PDF
              pdf.set_font("Arial", size=10)
              for chat in chat_history:
                  pdf.cell(200, 10, txt=f"Query: {chat.get('query', 'N/A')}", ln=True)
                  pdf.multi_cell(0, 10, txt=f"Response: {chat.get('response', 'N/A')}")
                  pdf.ln(5)
      
              # Save the PDF to memory or Cloud Storage
              pdf_file_name = f"{user_id}_wellness_plan.pdf"
              bucket_name = "getufit"  # Replace with your Cloud Storage bucket name
      
              # Upload PDF to Cloud Storage
              bucket = storage_client.bucket(bucket_name)
              blob = bucket.blob(pdf_file_name)
              blob.upload_from_string(pdf.output(dest="S").encode("latin1"), content_type="application/pdf")
      
              pdf_url = f"https://storage.googleapis.com/{bucket_name}/{pdf_file_name}"
              return jsonify({"message": "PDF generated successfully.", "pdf_url": pdf_url})
      
          except Exception as e:
              logging.error(f"Error in /generate_pdf: {e}")
              return jsonify({"error": str(e)}), 500
      @app.route("/download_pdf", methods=["GET"])
      def download_pdf():
          user_id = request.args.get("user_id")
          if not user_id:
              return jsonify({"error": "user_id is required"}), 400
      
          bucket_name = "getufit"
          pdf_file_name = f"{user_id}_wellness_plan.pdf"
      
          try:
              bucket = storage_client.bucket(bucket_name)
              blob = bucket.blob(pdf_file_name)
      
              if not blob.exists():
                  return jsonify({"error": "PDF not found"}), 404
      
              signed_url = blob.generate_signed_url(
                  version="v4",
                  expiration=timedelta(minutes=15),
                  method="GET",
              )
              return jsonify({"pdf_url": signed_url})
      
          except Exception as e:
              logging.error(f"Error in /download_pdf: {e}")
              return jsonify({"error": str(e)}), 500
      
      
      
      
      @app.route("/fetch_user_from_bigquery", methods=["GET"])
      def fetch_user_from_bigquery():
          """Fetch user data from BigQuery."""
          try:
              user_id = request.args.get("user_id")
              if not user_id:
                  return jsonify({"error": "user_id is required"}), 400
      
              # Query BigQuery for user data
              query = f"""
              SELECT *
              FROM `buildnblog.wellness_analytics.users`
              WHERE user_id = '{user_id}'
              """
              logging.debug(f"Executing BigQuery: {query}")
              query_job = bigquery_client.query(query)
              results = [dict(row) for row in query_job]
      
              if not results:
                  return jsonify({"error": "User not found in BigQuery"}), 404
      
              return jsonify({"user_data": results[0]})
      
          except Exception as e:
              logging.error(f"Error fetching user data from BigQuery: {e}")
              return jsonify({"error": str(e)}), 500
      # 
      
      @app.route("/generate_fitness_plan_from_bigquery", methods=["GET"])
      def generate_fitness_plan_from_bigquery():
          """Generate personalized fitness plan from BigQuery data."""
          try:
              user_id = request.args.get("user_id")
              if not user_id:
                  return jsonify({"error": "user_id is required"}), 400
      
              # Fetch user data from BigQuery
              query = f"""
              SELECT *
              FROM `buildnblog.wellness_analytics.users`
              WHERE user_id = '{user_id}'
              """
              query_job = bigquery_client.query(query)
              results = [dict(row) for row in query_job]
      
              if not results:
                  return jsonify({"error": "User not found in BigQuery"}), 404
      
              user_data = results[0]
              logging.debug(f"User data retrieved from BigQuery: {user_data}")
      
              # Generate fitness plan using AI
              ai_query = f"""
              Generate a personalized fitness plan for the following user:
              Name: {user_data['name']}
              Age: {user_data['age']}
              Height: {user_data['height']}
              Weight: {user_data['weight']}
              Goal: {user_data['goal']}
              Experience: {user_data['experience']}
              Health Issues: {user_data.get('health_issues', 'None')}
              The response must strictly adhere to this JSON structure:
              {{
                  "fitness_goal": "string",
                  "activities": [
                      {{
                          "day": "string",
                          "focus": "string",
                          "exercises": [
                              {{
                                  "name": "string",
                                  "sets": "integer",
                                  "reps": "string",
                                  "rest": "integer",
                                  "notes": "string (optional)"
                              }}
                          ]
                      }}
                  ],
                  "nutrition": "string"
              }}
              """
              ai_response = call_gemini(ai_query)
              logging.debug(f"Raw AI Response: {ai_response}")
      
              # Send the raw AI response to the frontend
              return jsonify({"raw_ai_response": ai_response})
      
          except Exception as e:
              logging.error(f"Error in /generate_fitness_plan_from_bigquery: {e}")
              return jsonify({"error": str(e)}), 500





         def sanitize_response(response):
             """Sanitize and validate the AI response for JSON compatibility."""
             if not response:
                 return "{}"  # Return an empty JSON if the response is None or empty.
         
             # Remove markdown code fences and extra whitespace.
             response = response.strip("```json").strip("```").strip()
         
             # Replace common issues like unquoted ranges.
             response = response.replace("8-12", '"8-12"')
             response = response.replace("10-15", '"10-15"')
             response = response.replace("30-60", '"30-60"')
         
             return response
         
         
         
         def call_gemini(query):
             """Call the Gemini model using Vertex AI to generate structured content."""
             try:
                 vertexai.init(project=credentials.project_id, location="us-central1", credentials=credentials)
                 model = GenerativeModel("gemini-1.5-pro-002")
                 response = model.generate_content([query], generation_config=generation_config, stream=False)
                 if hasattr(response, 'candidates') and response.candidates:
                     return response.candidates[0].content.parts[0].text
                 return None
             except Exception as e:
                 logging.error(f"Error calling Gemini: {e}")
                 return None
         
1. Rag model code:
    ```python
   from flask import Flask, request, jsonify
   import numpy as np
   from flask_cors import CORS
   import faiss
   import vertexai
   from google.cloud import aiplatform
   from vertexai.generative_models import GenerativeModel
   import logging
   import os
   import json
   import warnings
   from datetime import datetime
   from google.oauth2 import service_account
   from google.protobuf.json_format import MessageToDict
   from google.cloud import storage  # Import the GCS client library
   
   # Suppress specific future warnings that aren't critical to functionality
   warnings.filterwarnings("ignore", category=FutureWarning)
   
   # Setup logging for debugging
   logging.basicConfig(level=logging.INFO)
   
   # Initialize Flask app
   app = Flask(__name__)
   CORS(app)
   
   SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "getufit.json")
   os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
   if not os.path.exists(SERVICE_ACCOUNT_FILE):
       raise FileNotFoundError("Service account key file not found.")
   
   with open(SERVICE_ACCOUNT_FILE) as f:
       service_account_info = json.load(f)
   credentials = service_account.Credentials.from_service_account_info(
       service_account_info
   )
   
   # Initialize Vertex AI project
   vertexai.init(
       project="buildnblog", location="us-central1", credentials=credentials
   )
   
   # Vertex AI embedding endpoint
   EMBEDDING_MODEL_ENDPOINT = (
       "projects/buildnblog/locations/us-central1/"
       "publishers/google/models/textembedding-gecko"
   )
   
   # Embedding dimensions for textembedding-gecko
   embedding_dimension = 768
   
   # GCS bucket name
   GCS_BUCKET_NAME = "getufit1"
   
   # Initialize GCS client
   storage_client = storage.Client(
       credentials=credentials, project="buildnblog"
   )
   
   # Initialize the language model
   model = GenerativeModel("gemini-1.5-flash-002")
   
   # Initialize dictionary for patient data
   patients_data = {}
   
   
   # Function to ensure patient-specific data structures are set up
   def ensure_patient_data(patient_id):
       if patient_id not in patients_data:
           patients_data[patient_id] = {
               "text_index": faiss.IndexFlatL2(embedding_dimension),
               "text_documents": [],  # Holds dictionaries with 'text' and 'timestamp'
               "text_embeddings": [],
           }
   
   
   # Function to generate embeddings using Vertex AI
   def generate_gcp_embedding(text):
       """Generate embedding using GCP Vertex AI model."""
       if not isinstance(text, str) or not text.strip():
           raise ValueError("Text content for embedding must be a non-empty string.")
   
       prediction_client = aiplatform.gapic.PredictionServiceClient(
           client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"},
           credentials=credentials,
       )
       instance = {"content": text}
   
       try:
           response = prediction_client.predict(
               endpoint=EMBEDDING_MODEL_ENDPOINT, instances=[instance]
           )
           response_dict = MessageToDict(response._pb)
   
           predictions = response_dict.get("predictions")
           if not predictions:
               raise ValueError("No predictions found in response.")
   
           embeddings = predictions[0].get("embeddings")
           if embeddings is None:
               raise ValueError("Embeddings not found in response.")
   
           # Handle nested 'values' structure
           if isinstance(embeddings, dict) and "values" in embeddings:
               embedding_values = embeddings["values"]
           elif isinstance(embeddings, list):
               embedding_values = embeddings
           else:
               raise ValueError(f"Unexpected embeddings format: {embeddings}")
   
           # Convert values to float
           return np.array([float(value) for value in embedding_values], dtype=np.float32)
   
       except Exception as e:
           logging.error(f"Error generating embedding: {e}")
           raise
   
   
   
   
   # Function to upload data to GCS
   def upload_to_gcs(bucket_name, destination_blob_name, data):
       """Uploads data to the bucket."""
       bucket = storage_client.bucket(bucket_name)
       blob = bucket.blob(destination_blob_name)
       blob.upload_from_string(data)
       logging.info(
           f"Uploaded {destination_blob_name} to GCS bucket {bucket_name}."
       )
   
   
   # Function to download data from GCS
   def download_from_gcs(bucket_name, source_blob_name):
       """Downloads data from the bucket."""
       bucket = storage_client.bucket(bucket_name)
       blob = bucket.blob(source_blob_name)
       data = blob.download_as_string()
       logging.info(
           f"Downloaded {source_blob_name} from GCS bucket {bucket_name}."
       )
       return data
   
   
   # Function to save embeddings and documents to GCS
   def save_patient_data_to_gcs(patient_id, data):
       # Save embeddings
       embeddings_blob_name = f"embeddings/{patient_id}/{patient_id}_embeddings.npy"
       embeddings_data = np.array(data["text_embeddings"], dtype=np.float32)
       # Convert numpy array to bytes
       embeddings_bytes = embeddings_data.tobytes()
       upload_to_gcs(GCS_BUCKET_NAME, embeddings_blob_name, embeddings_bytes)
   
       # Save documents
       documents_blob_name = f"documents/{patient_id}/{patient_id}_documents.json"
       # Serialize documents to JSON string
       documents_json = json.dumps(data["text_documents"], default=str)
       upload_to_gcs(GCS_BUCKET_NAME, documents_blob_name, documents_json)
   
   
   # Function to load embeddings and documents from GCS
   def load_patient_data_from_gcs(patient_id):
       data = patients_data[patient_id]
   
       # Load embeddings
       embeddings_blob_name = f"embeddings/{patient_id}/{patient_id}_embeddings.npy"
       try:
           embeddings_bytes = download_from_gcs(
               GCS_BUCKET_NAME, embeddings_blob_name
           )
           embeddings_data = np.frombuffer(
               embeddings_bytes, dtype=np.float32
           ).reshape(-1, embedding_dimension)
           data["text_embeddings"] = embeddings_data.tolist()
           # Reconstruct FAISS index
           data["text_index"].add(embeddings_data)
       except Exception as e:
           logging.info(
               f"No embeddings found in GCS for patient {patient_id}: {e}"
           )
   
       # Load documents
       documents_blob_name = f"documents/{patient_id}/{patient_id}_documents.json"
       try:
           documents_json = download_from_gcs(
               GCS_BUCKET_NAME, documents_blob_name
           )
           data["text_documents"] = json.loads(documents_json)
       except Exception as e:
           logging.info(
               f"No documents found in GCS for patient {patient_id}: {e}"
           )
   
   
   # Function to insert text documents for a specific patient
   def insert_text_documents(patient_id, documents):
       ensure_patient_data(patient_id)
       data = patients_data[patient_id]
   
       # Load existing data from GCS
       load_patient_data_from_gcs(patient_id)
   
       for doc in documents:
           raw_text = doc["text"]
           
           # Serialize the text if it's a dictionary
           if isinstance(raw_text, dict):
               text = json.dumps(raw_text, indent=2)  # Convert to a JSON-formatted string
           else:
               text = raw_text
   
           if not isinstance(text, str) or not text.strip():
               logging.error("Text field must be a non-empty string.")
               continue
   
           logging.info(f"Inserting document text: {text}")
           timestamp = datetime.now().isoformat()
   
           # Generate embedding using Vertex AI
           embedding = generate_gcp_embedding(text)
   
           data["text_documents"].append({"text": text, "timestamp": timestamp})
           data["text_embeddings"].append(embedding.tolist())
   
           # Add the embedding to the FAISS index
           data["text_index"].add(np.array([embedding]).astype(np.float32))
   
       # Save embeddings and documents to GCS
       save_patient_data_to_gcs(patient_id, data)
   
   
   # Route for adding data
   @app.route("/add_data", methods=["POST"])
   def add_data():
       content = request.json
       patient_id = content.get("patient_id")
       documents = content.get("documents", [])
   
       # Validate patient_id
       if not patient_id:
           return jsonify({"error": "Patient ID is required."}), 400
   
       # Validate documents
       if not documents:
           return jsonify({"error": "Documents are required."}), 400
   
       for doc in documents:
           if not doc.get("text"):
               return jsonify({"error": "Each document must have a non-empty 'text' field."}), 400
   
       # Insert validated documents
       insert_text_documents(patient_id, documents)
   
       return jsonify({"message": "Data added successfully"}), 200
   
   
   # Function to retrieve top documents for a specific patient
   def retrieve_top_text_documents(patient_id, query, top_n=3):
       ensure_patient_data(patient_id)
       data = patients_data[patient_id]
   
       # Load existing data from GCS if not already loaded
       if data["text_index"].ntotal == 0:
           load_patient_data_from_gcs(patient_id)
   
       if data["text_index"].ntotal == 0:
           logging.info(
               f"No embeddings found for patient {patient_id}. "
               "Please add documents first."
           )
           return []
   
       # Generate query embedding using Vertex AI
       query_embedding = generate_gcp_embedding(query)
       query_embedding = np.array([query_embedding]).astype(np.float32)
   
       distances, indices = data["text_index"].search(query_embedding, top_n)
   
       retrieved_docs = [
           data["text_documents"][int(index)]["text"]
           for index in indices[0]
           if 0 <= index < len(data["text_documents"])
       ]
   
       return retrieved_docs
   
   
   # Function to retrieve the latest document for a patient by timestamp
   def retrieve_latest_document(patient_id):
       ensure_patient_data(patient_id)
       data = patients_data[patient_id]
   
       # Load existing data from GCS if not already loaded
       if not data["text_documents"]:
           load_patient_data_from_gcs(patient_id)
   
       if not data["text_documents"]:
           return "No health records available."
   
       # Find the latest document by timestamp
       latest_document = max(
           data["text_documents"], key=lambda x: x["timestamp"]
       )
       return latest_document["text"]
   
   
   # Set generation configuration
   generation_config = {
       "max_output_tokens": 4024,
       "temperature": 0.7,
       "top_p": 0.9,
   }
   
   
   # Function to handle the RAG pipeline for a specific patient
   def rag_pipeline(
       patient_id, query, conversation_context="", top_n=3
   ):
       ensure_patient_data(patient_id)
   
       # Check if the query specifically asks for the latest issue
       if "latest health issue" in query.lower():
           return retrieve_latest_document(patient_id)
   
       # Retrieve relevant documents
       retrieved_docs = retrieve_top_text_documents(
           patient_id, query, top_n
       )
   
       # If no docs retrieved, fall back to query-only response
       if not retrieved_docs:
           response = model.start_chat().send_message(
               query, generation_config=generation_config
           )
           return response.text
   
       # Use all retrieved docs as context for generating a response
       context = "\n".join(retrieved_docs)
       full_context = (
           f"{conversation_context}\nRelevant Information:\n"
           f"{context}\n\nQuestion:\n{query}"
       )
   
       response = model.start_chat().send_message(
           full_context, generation_config=generation_config
       )
       return response.text
   
   
   # Route for chatting with the bot
   @app.route("/chat", methods=["POST"])
   def chat():
       content = request.json
       patient_id = content["patient_id"]
       query = content["query"]
   
       conversation_context = content.get("conversation_context", "")
   
       # Get response from RAG pipeline
       response = rag_pipeline(
           patient_id, query, conversation_context
       )
   
       return jsonify({"response": response}), 200
   
   
   # Run the Flask app
   if __name__ == "__main__":
       port = int(os.environ.get("PORT", 8081))
       app.run(host="0.0.0.0", port=port)
   
   @app.route("/")
   def health_check():
       """Health check endpoint."""
       return jsonify({"status": "Backend is running!"})
   
   if __name__ == "__main__":
       app.run(host="0.0.0.0", port=8080)
       ```

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


## Conclusion
The frontend, in combination with the backend and GCP services, delivers a complete solution for personalized fitness and wellness assistance. By leveraging Next.js and React, the application is fast, responsive, and user-friendly, making it an excellent tool for fitness enthusiasts.


