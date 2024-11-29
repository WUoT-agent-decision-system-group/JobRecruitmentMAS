FROM python:3.10 AS spade
WORKDIR /app
RUN pip install spade
RUN pip install pymongo
RUN pip install dependency_injector

FROM spade
WORKDIR /app
COPY . /app
ENV PYTHONPATH="/app/"
RUN chmod +x app/main.py
CMD python -u app/main.py
