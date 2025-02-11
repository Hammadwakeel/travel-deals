from pydantic import BaseModel, Field
from typing import List, Dict

# ---------------------------
# Flight Search Model
# ---------------------------
class FlightSearchRequest(BaseModel):
    origin_location_code: str = Field(..., alias="originLocationCode", example="JFK")
    destination_location_code: str = Field(..., alias="destinationLocationCode", example="LHR")
    departure_date: str = Field(..., alias="departureDate", example="2025-03-01")
    return_date: str = Field(..., alias="returnDate", example="2025-03-10")
    adults: int = Field(1, example=1)
    children: int = Field(0, example=1)
    infants: int = Field(0, example=0)
    travel_class: str = Field(..., alias="travelClass", example="ECONOMY")
    currency_code: str = Field(..., alias="currencyCode", example="USD")
    max_price: int = Field(..., alias="maxPrice", example=1500)
    max: int = Field(1, example=2)

    class Config:
        populate_by_name = True

# ---------------------------
# New Models for Vehicle Search
# ---------------------------
class FlightSegment(BaseModel):
    transportationType: str = Field(..., example="FLIGHT")
    transportationNumber: str = Field(..., example="AF380")
    departure: Dict[str, str] = Field(
        ..., 
        example={"localDateTime": "2024-04-10T09:00:00", "iataCode": "NCE"}
    )
    arrival: Dict[str, str] = Field(
        ..., 
        example={"localDateTime": "2024-04-10T10:00:00", "iataCode": "CDG"}
    )

class PassengerCharacteristic(BaseModel):
    passengerTypeCode: str = Field(..., example="ADT")
    age: int = Field(..., example=20)

class VehicleSearchRequest(BaseModel):
    startLocationCode: str = Field(..., example="CDG")
    endAddressLine: str = Field(..., example="Avenue Anatole France, 5")
    endCityName: str = Field(..., example="Paris")
    endZipCode: str = Field(..., example="75007")
    endCountryCode: str = Field(..., example="FR")
    endName: str = Field(..., example="Souvenirs De La Tour")
    endGeoCode: str = Field(..., example="48.859466,2.2976965")
    transferType: str = Field(..., example="PRIVATE")
    startDateTime: str = Field(..., example="2024-04-10T10:30:00")
    passengers: int = Field(..., example=2)
    stopOvers: List = Field(default_factory=list)
    startConnectedSegment: FlightSegment
    passengerCharacteristics: List[PassengerCharacteristic]
