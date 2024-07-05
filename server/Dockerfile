# Use an official Python runtime as a parent image
FROM zamafhe/concrete-ml:latest

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5001

CMD ["python", "./app.py"]