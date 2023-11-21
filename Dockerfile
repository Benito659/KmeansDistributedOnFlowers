FROM python:3.10.5

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN py 

COPY . /app

EXPOSE 5000

CMD ["python", "/app/app.py"]