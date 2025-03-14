# Use an official Python runtime as a parent image
FROM python

# Set the working directory
WORKDIR /

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app
COPY . .

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
