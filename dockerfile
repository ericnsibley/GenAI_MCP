FROM python:3.12-slim

WORKDIR /app

ENV PORT=8060

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python data_load.py && rm -rf /zillow_data
EXPOSE $PORT 
CMD ["sh", "-c", "cd chat_app && uvicorn chat_server:app --host 0.0.0.0 --port $PORT"] 