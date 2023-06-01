FROM python:3.8

WORKDIR /api

COPY requirements.txt /api

RUN pip install -r requirements.txt

EXPOSE 8000

RUN chmod 755 ./entrypoint.sh

CMD ["./entrypoint.sh"]
