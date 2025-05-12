# Military Organization Management System API 
 
This is a Django REST API backend for a military organization management system. It provides a complete backend solution for managing members, units, events, training, operations, and more. 
 
## Features 
 
- Discord OAuth integration 
- JWT-based authentication 
- Role-based access control 
- Unit and position management 
- Event management with calendar integration 
- Training certificates 
- Ship management 
- Operation orders 
- Standards/SOPs documentation 
- Forums and discussions 
- Member onboarding and progression 
 
## Tech Stack 
 
- Django 4.2 
- Django REST Framework 
- PostgreSQL 
- Docker 
- AWS S3 for media storage (optional) 
 
## Getting Started 
 
### Prerequisites 
 
- Docker and Docker Compose 
- A Discord Application for OAuth integration 
 
### Installation and Setup 
 
1. Clone this repository 
 
2. Copy the `.env.example` file to `.env` and update the values: 
   ``` 
   cp .env.example .env 
   ``` 
 
3. Build and run the Docker containers: 
   ``` 
   docker-compose up -d --build 
   ``` 
 
4. Access the API at http://localhost:8000/api/ 
 
## API Documentation 
 
The API provides endpoints for the following resources: 
 
- Users and Authentication 
- Units, Branches, and Positions 
- Events and Attendance 
- Operation Orders 
- Training Certificates 
- Ships and Fleet Management 
- Forums and Discussions 
- Standards/SOPs 
- Applications and Onboarding 
 
## Development 
 
### Running Tests 
 
``` 
docker-compose run web python manage.py test 
``` 
 
### Creating Migrations 
 
``` 
docker-compose run web python manage.py makemigrations 
docker-compose run web python manage.py migrate 
``` 
 
### Creating a Superuser 
 
``` 
docker-compose run web python manage.py createsuperuser 
``` 
 
## Deployment 
 
For production deployment, update the `.env` file with production settings and use the provided Dockerfile. 
 
## License 
 
This project is licensed under the MIT License - see the LICENSE file for details. 
