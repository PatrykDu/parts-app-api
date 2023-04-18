# parts-app-api

**DRF (Django REST Framework) api project**

  

# Endpoints

## /api/user
 - **/user/create/**
   - POST - Register a new user
 - **/user/token**
    - POST - Create new token
 - **/user/me**
    - PUT - Update whole user
    - PATCH - Update some fields of user
    - GET - View profile
## /api/vehicles
 - **/vehicles/**
   - GET - List all vehicles
   - POST - Create vehicle
 - **/vehicles/*<vehicle_id>*/**
    - GET - View details of vehicle
    - PUT - Update whole vehicle
    - PATCH - Update some fields of vehicle
    - DELETE - Delete vehicle