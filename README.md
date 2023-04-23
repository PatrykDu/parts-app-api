**DRF (Django REST Framework) API used to store information about tuned vehicles. Multiple users can store information about their vehicles with photos and installed parts along with all costs.**

### [Swagger API Schema](https://github.com/PatrykDu/parts-app-api#swagger-ui-schema "Heading link")
#
# Endpoints

## /api/user
 - **/user/create/**
   - POST - Register a new user
 - **/user/token/**
    - POST - Create new token
 - **/user/me/**
    - GET - View profile
    - PUT - Update whole user
    - PATCH - Update some fields of user
## /api/vehicle
 - **/vehicle/vehicles/**
    - GET - List all vehicles
         
   ###
         Flag parameters in request for filtering:
         parts=<part_id>
         tags=<tag_id>

    - POST - Create vehicle
   

 - **/vehicle/*<vehicle_id>*/**
    - GET - View details of vehicle
    - PUT - Update whole vehicle
    - PATCH - Update some fields of vehicle
    - DELETE - Delete vehicle
 - **/vehicle/parts/*<vehicle_id>*/upload-image/**
    - POST - Upload image
 - **/vehicle/tags/**
    - GET - List all tags
   ###
         Flag parameters in request for filtering:
         assigned_only=0    - show all
         assigned_only=1    - show only assigned to vehicle

    - POST - Create tag
    - PUT/PATCH - Update tags
    - DELETE - Delete tags
 - **/vehicle/parts/**
    - GET - List all parts
   ###
         Flag parameters in request for filtering:
         assigned_only=0    - show all parts assigned and unassigned to vehicle
         assigned_only=1    - show parts only assigned to any vehicle

    - POST - Create part
 - **/vehicle/parts/*<part_id>*/**
    - GET - View details of part
    - PUT - Update whole part
    - PATCH - Update some fields of part
    - DELETE - Delete part

#
#

# Swagger UI Schema:
![Swagger Schema](https://github.com/PatrykDu/parts-app-api/blob/main/.github/pictures/API_schema.png?raw=true)