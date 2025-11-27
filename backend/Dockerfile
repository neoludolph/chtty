FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . . 
EXPOSE 8001
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--reload" ]