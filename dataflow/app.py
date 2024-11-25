from google.cloud import firestore, bigquery
from google.oauth2 import service_account
from datetime import datetime, timezone

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "./getufit.json"

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

# Initialize Firestore and BigQuery clients with the credentials
firestore_client = firestore.Client(credentials=credentials, project=credentials.project_id)
bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)

def firestore_to_bigquery():
    try:
        # Firestore collection reference
        users_collection_ref = firestore_client.collection("users")

        # Query Firestore documents for users
        users_docs = users_collection_ref.stream()

        # Prepare rows for BigQuery
        user_rows_to_insert = []
        chat_rows_to_insert = []

        for user_doc in users_docs:
            user_data = user_doc.to_dict()
            user_id = user_doc.id  # Firestore document ID acts as user_id

            if user_data:
                # Add user profile data to BigQuery
                user_rows_to_insert.append({
                    "user_id": user_id,
                    "name": user_data.get("name", ""),
                    "age": user_data.get("age", None),
                    "gender": user_data.get("gender", ""),
                })

                # Fetch chat history subcollection for this user
                chats_ref = users_collection_ref.document(user_id).collection("chats")
                chat_docs = chats_ref.stream()

                for chat_doc in chat_docs:
                    chat_data = chat_doc.to_dict()
                    # Convert Firestore timestamp to ISO format
                    timestamp = chat_data.get("timestamp", datetime.now(timezone.utc))
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.isoformat()

                    chat_rows_to_insert.append({
                        "user_id": user_id,
                        "query": chat_data.get("query", ""),
                        "response": chat_data.get("response", ""),
                        "timestamp": timestamp,
                    })

        # Debugging: Print rows
        print("User Rows to insert:", user_rows_to_insert)
        print("Chat Rows to insert:", chat_rows_to_insert)

        # Skip BigQuery insertion if no rows are present
        if not user_rows_to_insert and not chat_rows_to_insert:
            print("No data to insert into BigQuery.")
            return

        # BigQuery table IDs
        user_table_id = "buildnblog.wellness_analytics.users"
        chat_table_id = "buildnblog.wellness_analytics.chat_history"

        # Insert rows into BigQuery
        if user_rows_to_insert:
            user_errors = bigquery_client.insert_rows_json(user_table_id, user_rows_to_insert)
            if user_errors:
                print(f"Encountered errors while inserting users: {user_errors}")
            else:
                print("User data successfully written to BigQuery!")

        if chat_rows_to_insert:
            chat_errors = bigquery_client.insert_rows_json(chat_table_id, chat_rows_to_insert)
            if chat_errors:
                print(f"Encountered errors while inserting chats: {chat_errors}")
            else:
                print("Chat data successfully written to BigQuery!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    firestore_to_bigquery()
