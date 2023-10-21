FROM python:3.11-slim

RUN mkdir /code
WORKDIR /code

RUN pip install pipenv
COPY ./Pipfile* /code
RUN pipenv install

COPY ./ /code

CMD [ "pipenv", "run", "gunicorn", "-w", "4", "haiku:app", "-c", "config/gunicorn_conf.py" ]
