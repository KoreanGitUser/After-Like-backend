FROM python:3.9.12

WORKDIR /app
COPY . /app
COPY ./requirements.txt /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8050" ]