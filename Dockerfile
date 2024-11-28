FROM python:3.10 AS spade
WORKDIR /app
RUN pip install spade

FROM spade
WORKDIR /app
COPY . /app
RUN chmod +x app/main.py
CMD python -u app/main.py
