FROM python:3.10 AS spade
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r ./requirements.txt

FROM spade
WORKDIR /app
COPY . /app
ENV PYTHONPATH="/app/"
RUN chmod +x app/main.py
CMD python -u app/main.py
