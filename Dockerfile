FROM python:3.11-slim

# Install dependencies for Chrome + Selenium
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    chromium chromium-driver

# Set env so Chrome runs headless
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/bin/chromium"

# Create app folder
WORKDIR /app

# Copy files
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Entry point
CMD ["python", "main.py"]
