# Use official Python image
FROM python:3.11

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the port used by Dash
EXPOSE 8050

# Start app with gunicorn, point to the correct file!
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "dashboard:server"]
