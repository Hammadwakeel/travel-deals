# Travel Deals API and Streamlit App

## Overview

This project is a travel search application that integrates a FastAPI backend with a Streamlit frontend to search for flight, hotel, and vehicle transfer deals using the Amadeus API. The app also leverages OpenAI's GPT-4 (via LangChain) to generate an engaging blog post summarizing the best deals across these categories. Users can search for flights, hotels, and vehicle transfer offers, and then view or download a formatted blog post (in Word or PDF format) containing the best deals.

## Features

- **Flight Search:** Retrieve flight offers using the Amadeus API.
- **Hotel Search:** Fetch hotel deals based on city, radius, ratings, etc.
- **Vehicle Transfer Offers:** Search for private transfer deals by supplying travel details.
- **Deals Post Generation:** Generate a blog post that combines flight, hotel, and vehicle deals using ChatOpenAI.
- **Download Options:** Download the generated blog post as a Word document or PDF.
- **User-friendly UI:** A Streamlit-based frontend for interactive searches and results display.

## Project Structure

├── app.py # Streamlit frontend code ├── main.py # FastAPI backend code ├── models.py # Pydantic models for flights and vehicles ├── config.py # Configuration file (e.g., Amadeus API credentials) ├── requirements.txt # List of Python dependencies └── README.md # This README file


## Installation

1. **Clone the repository:**

   ```bash
   https://github.com/Hammadwakeel/travel-deals.git

   cd travel-deals-app

   Create and activate a virtual environment (recommended):

python -m venv myenv
source myenv/bin/activate   # On Windows: myenv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

Configuration

    Amadeus API:
    Configure your Amadeus API credentials in the config.py file.

    OpenAI API Key:
    Set the OPENAI_API_KEY environment variable to your OpenAI API key:

    export OPENAI_API_KEY=your_openai_api_key_here

    PDF Font:
    Ensure that the DejaVuSans.ttf font file is located in the project directory (required for Unicode PDF generation using FPDF).

Running the Application
Start the FastAPI Backend

Run the following command from your project directory:

uvicorn main:app --reload

The backend will be accessible at http://127.0.0.1:8000.
Start the Streamlit Frontend

Open a new terminal window (with your virtual environment activated) and run:

streamlit run app.py

The Streamlit app will open in your default web browser.
Usage

    Enter Flight and Hotel Search Parameters:
    Use the form in the Streamlit app to specify flight search details (origin, destination, dates, etc.) and hotel search parameters (city code, radius, ratings, etc.).

    Enter Vehicle Search Parameters:
    Provide travel details for vehicle transfer offers (start location, destination address, transfer type, etc.) in the dedicated "Vehicle Search Parameters" section.

    Generate Deals Post:
    Upon clicking the "Get Best Deals" button, the app will:
        Send the flight search details in the request body.
        Send hotel search and vehicle data (vehicle data is JSON-encoded and added as a query parameter) to the FastAPI /deals endpoint.
        The backend fetches flight, hotel, and vehicle offers, builds a prompt, and calls OpenAI's GPT-4 to generate an engaging blog post summarizing the top deals.
        The generated post is displayed in the app and can be downloaded as a Word document or PDF.

API Endpoints

    GET /flights:
    Retrieve flight offers based on search parameters.

    GET /hotels:
    Retrieve hotel deals based on query parameters.

    POST /deals:
    Generate a deals blog post that incorporates flight, hotel, and vehicle offers.
        Request Body: Flight search parameters (FlightSearchRequest model).
        Query Parameters: Hotel search parameters and a JSON-encoded vehicle payload (under the key vehicle), along with top_k.

    POST /vehicle:
    (Standalone) Retrieve vehicle transfer offers using user-supplied travel information (VehicleSearchRequest model).

Dependencies

    FastAPI
    Uvicorn
    Streamlit
    Python-docx
    FPDF
    LangChain (for ChatOpenAI)
    Amadeus Python SDK (or equivalent)

Refer to requirements.txt for the full list of dependencies.

Acknowledgements

    Amadeus API
    FastAPI
    Streamlit
    OpenAI
    LangChain
    Python-docx



