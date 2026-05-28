FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Run the app
ENTRYPOINT [ "python", "-m", "app.main", "data/customers.csv", "data/subscriptions.csv", "output.json"]