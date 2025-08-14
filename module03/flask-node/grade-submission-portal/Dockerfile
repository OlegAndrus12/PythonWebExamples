# base image
FROM python:3.13-slim

## work directory
WORKDIR /app

# handle dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# EXPOSE THE CONTAINER PORT
EXPOSE 5001

CMD ["python", "app.py"]
