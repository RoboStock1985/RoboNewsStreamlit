import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

session = supabase_client.auth.get_session()
if session:
    st.session_state.user = session.user


def get_authenticated_client() -> Client:

    """Get an authenticated Supabase client using session tokens."""

    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    if session:
        # TODO - add try except block to handle missing session tokens
        try:
            access_token = session['access_token']
            refresh_token = session['refresh_token']

            if access_token:
                supabase_client.auth.set_session(access_token, refresh_token)

        except (KeyError, ValueError, RuntimeError):
            return supabase_client

    return supabase_client


def get_all_records(authenticated_supabase_client: Client, table_name: str, columns: list = None):

    """Fetch all records from the Supabase database."""

    # add in optional columms selection
    if columns:
        data = authenticated_supabase_client.table(table_name).select(",".join(columns)).execute()
    else:
        data = authenticated_supabase_client.table(table_name).select("*").execute()

    return data


def add_record(authenticated_supabase_client: Client,
               table_name: str, record: dict):

    """Add a new record to the Supabase database."""

    authenticated_supabase_client.table(table_name).insert(record).execute()


def update_record(authenticated_supabase_client: Client,
                  table_name: str, id: int, updated_data: dict):

    """Update a record in the Supabase database by its ID."""

    authenticated_supabase_client.table(table_name).update(updated_data).eq("book_id", id).execute()


def delete_record_by_id(authenticated_supabase_client: Client,
                        table_name: str, id: int, id_field: str):

    """Update a record in the Supabase database by its ID."""

    authenticated_supabase_client.table(table_name).delete().eq(f"{id_field}", id).execute()


def create_new_supabase_user(email: str, password: str):

    """Create a new user in the Supabase database."""

    # TODO - Add validation for username, email, and password
    # TODO - Add error handling for user creation

    authenticated_supabase_client = get_authenticated_client()

    try:
        auth_connection = authenticated_supabase_client.auth.sign_up({"email": email,"password": password,})
    except:
        return {"message": "Failed to create user. User may already exist.", "data": None}

    return {"message": "User created successfully.", "data": None}


def sign_in_user(authenticated_supabase_client: Client, email: str, password: str):

    """Sign in a user to the Supabase database."""

    # TODO - Add validation for username, email, and password
    # TODO - Add error handling for user sign-in

    authenticated_supabase_client.auth.sign_in_with_password({"email": email, "password": password})

    return authenticated_supabase_client


def check_session():

    """Check if a user session is active."""

    # check access token validity
    try:
        access_token = session['access_token']
        if access_token:
            return True
    except (KeyError, ValueError, RuntimeError):
        return False


def check_if_user_is_admin(authenticated_supabase_client: Client):

    """Check if the current user is an admin."""

    user = authenticated_supabase_client.auth.get_user()
    user_id = str(user.user.id)

    data = authenticated_supabase_client.table("users").select("is_admin").eq("user_id", user_id).execute()

    if data.data and data.data[0]['is_admin']:
        return True
    else:
        return False


if __name__ == "__main__":

    authenticated_supabase_client = get_authenticated_client()