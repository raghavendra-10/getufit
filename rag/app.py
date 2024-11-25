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
