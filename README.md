# parts-app-api

**DRF (Django REST Framework) api project**

  

# Endpoints

## /api/user
 - **/user/create/**
   - POST - Register a new user
 - **/user/token**
    - POST - Create new token
 - **/user/me**
    - GET - View profile
    - PUT - Update whole user
    - PATCH - Update some fields of user
## /api/vehicles
 - **/vehicles/**
    - GET - List all vehicles
    - POST - Create vehicle
 - **/vehicles/*<vehicle_id>*/**
    - GET - View details of vehicle
    - PUT - Update whole vehicle
    - PATCH - Update some fields of vehicle
    - DELETE - Delete vehicle
 - **/vehicles/tags**
    - GET - List all tags
    - POST - Create tag
    - PUT/PATCH - Update tags
    - DELETE - Delete tags
 - **/vehicles/parts**
    - GET - List all parts
    - POST - Create part
 - **/vehicles/parts/*<part_id>*/**
    - GET - View details of part
    - PUT - Update whole part
    - PATCH - Update some fields of part
    - DELETE - Delete part