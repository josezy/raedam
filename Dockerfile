FROM python:3.7-slim-buster

# Configuratoin defaults
ENV RAEDAM_ROOT "/opt/raedam"
ENV DATA_DIR "$RAEDAM_ROOT/data"
ENV DJANGO_DIR "$RAEDAM_ROOT/raedamdjango"
# ENV HTTP_PORT "8000"
ENV DJANGO_USER "www-data"
ENV VENV_NAME ".venv-docker"

# Setup system environment variables neded for python to run smoothly
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create project directory & user
WORKDIR "$RAEDAM_ROOT"

# Setup python3 virtual env with poetry
COPY ./poetry.lock "$RAEDAM_ROOT/poetry.lock"
COPY ./poetry.toml "$RAEDAM_ROOT/poetry.toml"
COPY ./pyproject.toml "$RAEDAM_ROOT/pyproject.toml"

RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install
# ENV PATH="$RAEDAM_ROOT/$VENV_NAME/bin:${PATH}"

# USER "$DJANGO_USER"
ADD . "$RAEDAM_ROOT"
VOLUME "$DATA_DIR"
# EXPOSE "$HTTP_PORT"

CMD ["poetry", "run", "./$DJANGO_DIR/manage.py", "runserver", "0.0.0.0:8000"]
