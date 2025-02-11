from fastapi import FastAPI, HTTPException, Depends, Query, Body
from config import amadeus
from models import FlightSearchRequest, VehicleSearchRequest
from amadeus import ResponseError
from langchain_openai import ChatOpenAI
from typing import List
import os

# ---------------------------
# Helper function to instantiate the LLM
# ---------------------------
def get_llm(API_KEY):
    llm = ChatOpenAI(
        model="gpt-4o",     # Adjust the model name as needed
        temperature=0.7, 
        api_key=API_KEY
    )
    return llm

# ---------------------------
# FastAPI App Instance
# ---------------------------
app = FastAPI(title="Flights, Hotels, Vehicles and Deals API")

# ---------------------------
# Flights Endpoint
# ---------------------------
@app.get("/flights", summary="Search for flight offers")
async def get_flights(search: FlightSearchRequest = Depends()):
    """
    Search for flight offers using provided parameters.
    """
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=search.origin_location_code,
            destinationLocationCode=search.destination_location_code,
            departureDate=search.departure_date,
            returnDate=search.return_date,
            adults=search.adults,
            children=search.children,
            infants=search.infants,
            travelClass=search.travel_class,
            currencyCode=search.currency_code,
            maxPrice=search.max_price,
            max=search.max
        )
        return {"data": response.data}
    except ResponseError as error:
        status_code = error.response.status_code if error.response else 500
        detail = error.response.body if error.response else str(error)
        raise HTTPException(status_code=status_code, detail=detail)

# ---------------------------
# Hotels Endpoint
# ---------------------------
@app.get("/hotels", summary="Search for hotels")
async def get_hotels(
    city_code: str = Query(..., alias="cityCode", example="PAR"),
    radius: int = Query(..., example=20),
    radius_unit: str = Query(..., alias="radiusUnit", example="KM"),
    ratings: List[str] = Query(..., example=["1", "2", "3", "4", "5"]),
    hotel_source: str = Query(..., alias="hotelSource", example="ALL")
):
    try:
        hotels_response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code,
            radius=radius,
            radiusUnit=radius_unit,
            ratings=ratings,
            hotelSource=hotel_source
        )
        return {"data": hotels_response.data}
    except ResponseError as error:
        status_code = error.response.status_code if error.response else 500
        detail = error.response.body if error.response else str(error)
        raise HTTPException(status_code=status_code, detail=detail)

# ---------------------------
# Deals Endpoint (Flights + Hotels + Vehicle)
# ---------------------------
@app.post("/deals", summary="Generate a blog post with top flight, hotel, and vehicle deals")
async def get_best_deals(
    # Flight search parameters from the request body
    flight_search: FlightSearchRequest = Body(...),
    # Hotel parameters (and top_k) as query parameters:
    city_code: str = Query(..., alias="cityCode", example="PAR"),
    radius: int = Query(..., example=20),
    radius_unit: str = Query(..., alias="radiusUnit", example="KM"),
    ratings: List[str] = Query(..., example=["1", "2", "3", "4", "5"]),
    hotel_source: str = Query(..., alias="hotelSource", example="ALL"),
    top_k: int = Query(3, example=3)
):
    """
    Calls flight, hotel, and vehicle search APIs, then passes their responses to the LLM
    with a prompt asking it to generate an engaging blog post that highlights the top
    k best deals in each category.
    """
    # Get flight deals
    try:
        flight_response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=flight_search.origin_location_code,
            destinationLocationCode=flight_search.destination_location_code,
            departureDate=flight_search.departure_date,
            returnDate=flight_search.return_date,
            adults=flight_search.adults,
            children=flight_search.children,
            infants=flight_search.infants,
            travelClass=flight_search.travel_class,
            currencyCode=flight_search.currency_code,
            maxPrice=flight_search.max_price,
            max=flight_search.max
        )
    except ResponseError as error:
        status_code = error.response.status_code if error.response else 500
        detail = error.response.body if error.response else str(error)
        raise HTTPException(status_code=status_code, detail=f"Flight API error: {detail}")

    # Get hotel deals
    try:
        hotel_response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code,
            radius=radius,
            radiusUnit=radius_unit,
            ratings=ratings,
            hotelSource=hotel_source
        )
    except ResponseError as error:
        status_code = error.response.status_code if error.response else 500
        detail = error.response.body if error.response else str(error)
        raise HTTPException(status_code=status_code, detail=f"Hotel API error: {detail}")

    # Get vehicle deals using a predefined travel request
    travel_request = {
        "startLocationCode": "CDG",
        "endAddressLine": "Avenue Anatole France, 5",
        "endCityName": "Paris",
        "endZipCode": "75007",
        "endCountryCode": "FR",
        "endName": "Souvenirs De La Tour",
        "endGeoCode": "48.859466,2.2976965",
        "transferType": "PRIVATE",
        "startDateTime": "2024-04-10T10:30:00",
        "passengers": 2,
        "stopOvers": [],
        "startConnectedSegment": {
            "transportationType": "FLIGHT",
            "transportationNumber": "AF380",
            "departure": {
                "localDateTime": "2024-04-10T09:00:00",
                "iataCode": "NCE"
            },
            "arrival": {
                "localDateTime": "2024-04-10T10:00:00",
                "iataCode": "CDG"
            }
        },
        "passengerCharacteristics": [
            {"passengerTypeCode": "ADT", "age": 20},
            {"passengerTypeCode": "CHD", "age": 10}
        ]
    }
    try:
        vehicle_response = amadeus.request("POST", "/v1/shopping/transfer-offers", travel_request)
    except ResponseError as error:
        status_code = error.response.status_code if error.response else 500
        detail = error.response.body if error.response else str(error)
        raise HTTPException(status_code=status_code, detail=f"Vehicle API error: {detail}")

    # Build a combined prompt including flight, hotel, and vehicle data
    prompt = (
        f"Based on the following data, create an engaging blog post that highlights the top {top_k} best flight deals, "
        f"the top {top_k} best hotel deals, and the top {top_k} best vehicle deals.\n\n"
        f"Flight Deals Data: {flight_response.data}\n\n"
        f"Hotel Deals Data: {hotel_response.data}\n\n"
        f"Vehicle Deals Data: {vehicle_response.data}\n\n"
        "Please include a clear ranking of the deals and highlight key details (such as prices, durations, locations, etc.) that make each option attractive."
    )

    # Retrieve the OpenAI API key from environment variables
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set in environment variables.")

    # Instantiate the LLM and generate the post
    llm = get_llm(API_KEY)
    response = llm.invoke(prompt)  # Adjust method (invoke/predict) per your langchain version
    post = response.content

    return {"post": post}

# ---------------------------
# Vehicle Deals Endpoint (Standalone)
# ---------------------------
@app.post("/vehicle", summary="Search for vehicle transfer offers using user travel information")
async def get_vehicle_deals(vehicle_search: VehicleSearchRequest = Body(...)):
    """
    Accepts user-provided travel information for a vehicle transfer offer and calls the Amadeus Transfer Offers API.
    """
    try:
        response = amadeus.request("POST", "/v1/shopping/transfer-offers", vehicle_search.dict())
        return {"data": response.data}
    except ResponseError as error:
        status_code = error.response.status_code if error.response else 500
        detail = error.response.body if error.response else str(error)
        raise HTTPException(status_code=status_code, detail=f"Vehicle API error: {detail}")
