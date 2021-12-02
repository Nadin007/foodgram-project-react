FROM python:3.9
COPY ./recipe_backend/requirements.txt /code/recipe_backend/requirements.txt
RUN python3 -m pip install --upgrade pip && pip3 install -r /code/recipe_backend/requirements.txt
COPY ./ /code
WORKDIR /code/recipe_backend/
CMD gunicorn recipe_backend.wsgi:application --bind 0.0.0.0:8000