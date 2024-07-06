FROM zamafhe/concrete-ml:latest

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["python", "./train_model.py"]