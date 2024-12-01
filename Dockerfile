FROM python:3.10 AS spade
WORKDIR /app
COPY ./requirements/common.txt /app
RUN pip install -r ./common.txt

FROM spade
WORKDIR /app
COPY . /app
ENV PYTHONPATH="/app/"
RUN chmod +x app/main.py
CMD python -u app/main.py
