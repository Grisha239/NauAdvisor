FROM python:3.11
ENV LANG C.UTF-8

RUN mkdir /bot

COPY requirements.txt /bot/requirements.txt
RUN pip install -r /bot/requirements.txt

WORKDIR /bot
COPY main.py /bot/main.py

CMD ["python", "main.py"]