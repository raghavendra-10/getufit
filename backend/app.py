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
        "You are a chatbot specialized in fitness, nutritionist and health wellness. "
        "You provide advice strictly related to fitness, nutrition, exercise routines, and wellness plans. "
        "Avoid any topics unrelated to fitness and health. "
        "If the user asks anything outside these topics, politely decline and redirect them to fitness-related inquiries.\n\n"
    )
    query = "{query}"+ base_prompt 
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

@app.route("/user", methods=["POST", "GET"])
def user():
    """Save or retrieve user profiles."""
    try:
        if request.method == "POST":
            # Save user profile
            user_data = request.json
            user_id = user_data.get("user_id")

            if not user_id:
                return jsonify({"error": "user_id is required"}), 400

            # Save or update user profile in Firestore
            firestore_client.collection("users").document(user_id).set(user_data)
            return jsonify({"message": "User profile saved successfully."})

        elif request.method == "GET":
            # Retrieve user profile
            user_id = request.args.get("user_id")
            if not user_id:
                return jsonify({"error": "user_id is required"}), 400

            user_doc = firestore_client.collection("users").document(user_id).get()
            if user_doc.exists:
                return jsonify(user_doc.to_dict())
            else:
                return jsonify({"error": "User not found"}), 404

    except Exception as e:
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
@app.route("/youtube_links", methods=["POST"])
def youtube_links():
    """Generate YouTube links for exercises using Gemini Pro."""
    try:
        # Get user input from request
        exercise_query = request.json.get("exercise")
        if not exercise_query:
            return jsonify({"error": "Exercise query is required"}), 400

        # Prompt to request YouTube links
        youtube_prompt = (
            f"Provide a list of the best YouTube video links for the following exercise: {exercise_query}. "
            "The videos should be high-quality tutorials or demonstrations, "
            "and return them in this JSON format: "
            "[{'title': 'Video Title', 'url': 'YouTube URL'}]"
        )

        # Call the Gemini API with the YouTube prompt
        response = gemini(youtube_prompt)

        # Log raw response for debugging
        logging.debug(f"Raw response from Gemini Pro: {response}")

        # Sanitize response
        response = response.strip("```json").strip("```").strip()

        # Parse the response
        try:
            video_links = json.loads(response)
            if isinstance(video_links, list):
                return jsonify({"videos": video_links})
            else:
                raise ValueError("Invalid response format")
        except json.JSONDecodeError:
            logging.error(f"Failed to parse response: {response}")
            return jsonify({"error": "Failed to parse response from Gemini Pro"}), 500

    except Exception as e:
        logging.error(f"Error in /youtube_links: {e}")
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
# @app.route("/generate_fitness_plan_from_bigquery", methods=["GET"])
# def generate_fitness_plan_from_bigquery():
#     """Generate personalized fitness plan from BigQuery data."""
#     try:
#         user_id = request.args.get("user_id")
#         if not user_id:
#             return jsonify({"error": "user_id is required"}), 400

#         # Fetch user data from BigQuery
#         query = f"""
#         SELECT *
#         FROM `buildnblog.wellness_analytics.users`
#         WHERE user_id = '{user_id}'
#         """
#         logging.debug(f"Executing BigQuery: {query}")
#         query_job = bigquery_client.query(query)
#         results = [dict(row) for row in query_job]

#         if not results:
#             return jsonify({"error": "User not found in BigQuery"}), 404

#         user_data = results[0]
#         logging.debug(f"User data retrieved from BigQuery: {user_data}")

#         # Generate fitness plan using AI
#         ai_query = f"""
#         Generate a personalized fitness plan for the following user:
#         Name: {user_data['name']}
#         Age: {user_data['age']}
#         Height: {user_data['height']}
#         Weight: {user_data['weight']}
#         Goal: {user_data['goal']}
#         Experience: {user_data['experience']}
#         Health Issues: {user_data.get('health_issues', 'None')}
#         Provide the plan in JSON format with keys 'fitness_goal' and 'activities'.
#         """
#         logging.debug(f"AI Query: {ai_query}")
#         ai_response = call_gemini(ai_query)
#         logging.debug(f"AI Response: {ai_response}")

#         # Parse AI response
#         try:
#             fitness_plan = json.loads(ai_response)
#             logging.debug(f"Parsed Fitness Plan: {fitness_plan}")
#         except json.JSONDecodeError as e:
#             logging.error(f"Error decoding AI response: {ai_response}. Error: {e}")
#             return jsonify({"error": "Failed to parse AI response"}), 500

#         # Save fitness plan to Firestore
#         firestore_client.collection("users").document(user_id).collection("fitness_plans").add(fitness_plan)

#         return jsonify(fitness_plan)

#     except Exception as e:
#         logging.error(f"Error in /generate_fitness_plan_from_bigquery: {e}")
#         return jsonify({"error": str(e)}), 500

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



# @app.route("/get_fitness_plan", methods=["GET"])
# def get_fitness_plan():
#     """Generate personalized fitness goals and activities based on user data."""
#     try:
#         user_id = request.args.get("user_id")
#         if not user_id:
#             return jsonify({"error": "user_id is required"}), 400

#         logging.debug(f"Fetching data for user_id: {user_id}")
#         # Fetch user data from Firestore
#         user_doc = firestore_client.collection("users").document(user_id).get()
#         print(user_doc,"user_doc")
#         if not user_doc.exists():
#             logging.debug(f"No user found for user_id: {user_id}")
#             return jsonify({"error": "User not found"}), 404
#         user_data = user_doc.to_dict()
#         logging.debug(f"User data: {user_data}")

#         # Use AI to generate activities and goals
#         query = f"""
#         Generate a personalized fitness plan for the following user:
#         Name: {user_data['name']}
#         Age: {user_data['age']}
#         Height: {user_data['height']}
#         Weight: {user_data['weight']}
#         Goal: {user_data['goal']}
#         Experience: {user_data['experience']}
#         Health Issues: {user_data.get('health_issues', 'None')}
#         Provide the plan in JSON format with keys 'fitness_goal' and 'activities'.
#         """
#         logging.debug(f"AI Query: {query}")
#         ai_response = call_gemini(query)
#         logging.debug(f"AI Response: {ai_response}")

#         # Parse the AI response as JSON
#         try:
#             fitness_plan = json.loads(ai_response)
#         except json.JSONDecodeError as e:
#             logging.error(f"Error decoding AI response: {ai_response}. Error: {e}")
#             return jsonify({"error": "Failed to parse AI response"}), 500

#         # Save the fitness plan to Firestore for future retrieval
#         firestore_client.collection("users").document(user_id).collection("fitness_plans").add(fitness_plan)

#         return jsonify(fitness_plan)

#     except Exception as e:
#         logging.error(f"Error in /get_fitness_plan: {e}")
#         return jsonify({"error": str(e)}), 500

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


@app.route("/get_saved_plan", methods=["GET"])
def get_saved_plan():
    """Retrieve a previously saved fitness plan."""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Fetch the latest fitness plan
        plans_ref = firestore_client.collection("users").document(user_id).collection("fitness_plans")
        plans = [doc.to_dict() for doc in plans_ref.stream()]

        if not plans:
            return jsonify({"error": "No fitness plan found for this user."}), 404

        # Return the most recent plan
        return jsonify(plans[-1])

    except Exception as e:
        logging.error(f"Error in /get_saved_plan: {e}")
        return jsonify({"error": str(e)}), 500

# def sanitize_response(response):
#     """Sanitize AI response for JSON compatibility."""
#     if not response:
#         return "{}"
#     response = response.replace("8-12", '"8-12"').replace("10-15", '"10-15"').replace("30-60", '"30-60"')
#     return response

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

# def call_gemini(query):
#     """Call the Gemini model using Vertex AI to generate activities."""
#     try:
#         vertexai.init(project=credentials.project_id, location="us-central1", credentials=credentials)
#         model = GenerativeModel("gemini-1.5-pro-002")
#         response = model.generate_content(
#             [query], generation_config=generation_config, stream=False
#         )
#         logging.debug(f"AI Response Object: {response}")
        
#         # Extract the content from the candidates attribute
#         if hasattr(response, 'candidates') and response.candidates:
#             ai_response_text = response.candidates[0].content.parts[0].text
#             logging.debug(f"Extracted AI Response Text: {ai_response_text}")
            
#             # Clean and return the response
#             cleaned_response = ai_response_text.strip("```json").strip("```").strip()
#             logging.debug(f"Cleaned AI Response Text: {cleaned_response}")
#             return cleaned_response
        
#         logging.error("Response does not contain 'candidates'.")
#         return "Error generating content. Please try again."
#     except Exception as e:
#         logging.error(f"Error calling Gemini AI: {e}")
#         return "Error generating content. Please try again."


@app.route("/")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
