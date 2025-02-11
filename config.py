# config.py
import os
from dotenv import load_dotenv
from amadeus import Client

# Load environment variables from the .env file
load_dotenv()

# Retrieve the credentials from the environment
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# Initialize the Amadeus API Client
amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)
