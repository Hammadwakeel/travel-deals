# app.py
import streamlit as st
import requests
import io
import docx
import json

# Define the base URL for your FastAPI backend
BASE_URL = "http://localhost:8000"

st.title("Travel Search App")
st.markdown("This app calls the FastAPI backend to search for flights, hotels, and generate a deals post including vehicle deals.")

# Initialize session state for the deals post if not already set
if "deals_post" not in st.session_state:
    st.session_state.deals_post = None

# ============================
# Deals Section
# ============================
st.header("Best Deals Post")

with st.form("deals_form"):
    st.subheader("Flight Search Parameters")
    col1, col2 = st.columns(2)
    with col1:
        origin_deals = st.text_input("Origin Airport Code", value="JFK", help="Example: JFK", key="origin_deals")
        departure_date_deals = st.text_input("Departure Date (YYYY-MM-DD)", value="2025-03-01", key="departure_date_deals")
        adults_deals = st.number_input("Number of Adults", value=1, step=1, key="adults_deals")
        children_deals = st.number_input("Number of Children", value=1, step=1, key="children_deals")
    with col2:
        destination_deals = st.text_input("Destination Airport Code", value="LHR", help="Example: LHR", key="destination_deals")
        return_date_deals = st.text_input("Return Date (YYYY-MM-DD)", value="2025-03-10", key="return_date_deals")
        infants_deals = st.number_input("Number of Infants", value=0, step=1, key="infants_deals")
        travel_class_deals = st.selectbox("Travel Class", options=["ECONOMY", "BUSINESS", "FIRST"], index=0, key="travel_class_deals")
    
    currency_deals = st.text_input("Currency Code", value="USD", key="currency_deals")
    max_price_deals = st.number_input("Maximum Price", value=1500, step=50, key="max_price_deals")
    max_offers_deals = st.number_input("Max Flight Offers", value=2, step=1, key="max_offers_deals")
    
    st.subheader("Hotel Search Parameters")
    city_code_deals = st.text_input("City Code", value="PAR", help="Example: PAR (Paris)", key="city_code_deals")
    radius_deals = st.number_input("Search Radius", value=20, step=1, key="radius_deals")
    radius_unit_deals = st.text_input("Radius Unit", value="KM", key="radius_unit_deals")
    ratings_deals_input = st.text_input("Ratings (comma separated)", value="1,2,3,4,5", key="ratings_deals_input")
    hotel_source_deals = st.text_input("Hotel Source", value="ALL", key="hotel_source_deals")
    
    st.subheader("Vehicle Search Parameters")
    v_startLocationCode = st.text_input("Start Location Code", value="CDG", key="v_startLocationCode")
    v_endAddressLine = st.text_input("End Address Line", value="Avenue Anatole France, 5", key="v_endAddressLine")
    v_endCityName = st.text_input("End City Name", value="Paris", key="v_endCityName")
    v_endZipCode = st.text_input("End Zip Code", value="75007", key="v_endZipCode")
    v_endCountryCode = st.text_input("End Country Code", value="FR", key="v_endCountryCode")
    v_endName = st.text_input("End Name", value="Souvenirs De La Tour", key="v_endName")
    v_endGeoCode = st.text_input("End GeoCode", value="48.859466,2.2976965", key="v_endGeoCode")
    v_transferType = st.selectbox("Transfer Type", options=["PRIVATE", "SHARED"], index=0, key="v_transferType")
    v_startDateTime = st.text_input("Start DateTime", value="2024-04-10T10:30:00", key="v_startDateTime")
    v_passengers = st.number_input("Passengers", value=2, step=1, key="v_passengers")
    
    st.subheader("Transportation Segment")
    v_transportationType = st.text_input("Transportation Type", value="FLIGHT", key="v_transportationType")
    v_transportationNumber = st.text_input("Transportation Number", value="AF380", key="v_transportationNumber")
    v_departure_localDateTime = st.text_input("Departure LocalDateTime", value="2024-04-10T09:00:00", key="v_departure_localDateTime")
    v_departure_iataCode = st.text_input("Departure IATA Code", value="NCE", key="v_departure_iataCode")
    v_arrival_localDateTime = st.text_input("Arrival LocalDateTime", value="2024-04-10T10:00:00", key="v_arrival_localDateTime")
    v_arrival_iataCode = st.text_input("Arrival IATA Code", value="CDG", key="v_arrival_iataCode")
    
    st.subheader("Passenger Characteristics")
    v_adt_age = st.number_input("Adult Age", value=20, step=1, key="v_adt_age")
    v_chd_age = st.number_input("Child Age", value=10, step=1, key="v_chd_age")
    
    top_k = st.number_input("Top K Deals", value=3, step=1, key="top_k")
    
    deals_submit = st.form_submit_button("Get Best Deals")

if deals_submit:
    with st.spinner("Fetching best deals, please wait..."):
        # Convert comma-separated ratings into a list for query parameters
        ratings_deals = [rating.strip() for rating in ratings_deals_input.split(",") if rating.strip()]
        
        # Flight search parameters will be sent as the JSON body
        flight_payload = {
            "originLocationCode": origin_deals,
            "destinationLocationCode": destination_deals,
            "departureDate": departure_date_deals,
            "returnDate": return_date_deals,
            "adults": adults_deals,
            "children": children_deals,
            "infants": infants_deals,
            "travelClass": travel_class_deals,
            "currencyCode": currency_deals,
            "maxPrice": max_price_deals,
            "max": max_offers_deals,
        }
        
        # Build hotel parameters (sent as query parameters)
        params = {
            "cityCode": city_code_deals,
            "radius": radius_deals,
            "radiusUnit": radius_unit_deals,
            "ratings": ratings_deals,
            "hotelSource": hotel_source_deals,
            "top_k": top_k,
        }
        
        # Build vehicle payload from the vehicle form inputs
        vehicle_payload = {
            "startLocationCode": v_startLocationCode,
            "endAddressLine": v_endAddressLine,
            "endCityName": v_endCityName,
            "endZipCode": v_endZipCode,
            "endCountryCode": v_endCountryCode,
            "endName": v_endName,
            "endGeoCode": v_endGeoCode,
            "transferType": v_transferType,
            "startDateTime": v_startDateTime,
            "passengers": v_passengers,
            "stopOvers": [],
            "startConnectedSegment": {
                "transportationType": v_transportationType,
                "transportationNumber": v_transportationNumber,
                "departure": {
                    "localDateTime": v_departure_localDateTime,
                    "iataCode": v_departure_iataCode
                },
                "arrival": {
                    "localDateTime": v_arrival_localDateTime,
                    "iataCode": v_arrival_iataCode
                }
            },
            "passengerCharacteristics": [
                {"passengerTypeCode": "ADT", "age": v_adt_age},
                {"passengerTypeCode": "CHD", "age": v_chd_age}
            ]
        }
        
        # Add the vehicle payload as a query parameter (encoded as a JSON string)
        params["vehicle"] = json.dumps(vehicle_payload)
        
        try:
            deals_response = requests.post(f"{BASE_URL}/deals", json=flight_payload, params=params)
            deals_response.raise_for_status()
            deals_data = deals_response.json()
            st.session_state.deals_post = deals_data.get("post", "No post returned.")
        except requests.RequestException as e:
            st.session_state.deals_post = f"Error contacting FastAPI backend for deals: {e}"
    st.success("Best deals fetched successfully!")

if st.session_state.deals_post:
    st.subheader("Generated Deals Post")
    st.write(st.session_state.deals_post)
    
    # ----- Create and provide download link for a Word document -----
    doc = docx.Document()
    doc.add_paragraph(st.session_state.deals_post)
    word_buffer = io.BytesIO()
    doc.save(word_buffer)
    word_buffer.seek(0)
    
    st.download_button(
        label="Download as Word Document",
        data=word_buffer,
        file_name="deals_post.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

