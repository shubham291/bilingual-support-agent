# 1. Start from a small Linux box that already has Python
FROM python:3.9-slim

# 2. Work inside a folder called /app
WORKDIR /app

# 3. Install the packages first (Docker remembers this step, so rebuilds are fast)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy your code
COPY . .

# 5. Start the API on port 8000
CMD ["fastapi", "run", "main.py", "--port", "8000"]