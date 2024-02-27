# Create MySQL DB

# Test Locally  
docker build -t dora-demo-image .
docker run -d -p 80:80 --name dora-demo-container dora-demo-image

# Onboarding API
curl -X POST -H "Content-Type: application/json" -d '{"app_name": "FlaskDemo-Docker", "deployment_count": 1, "deployment_status": "FAIL"}' http://127.0.0.1/insert-record

# Display Record
curl -X GET -H "Content-Type: application/json" -d '{"app_name": "online-library"}' http://127.0.0.1:80/display-record\n

# Display Application
curl http://localhost:8181/applications

# React UI 