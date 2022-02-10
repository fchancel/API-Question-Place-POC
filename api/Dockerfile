FROM python:3.9-slim

WORKDIR /app

RUN apt-get update; apt-get install bash -y

# Creating pip venv and adding it to PATH
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .


# use docker buildkit for caching the pip packages.
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:api", "--reload" ,"--host", "0.0.0.0", "--port", "8000"]