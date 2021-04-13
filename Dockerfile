FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY ./app /app
COPY requirements.txt requirements.txt
#RUN apk update
#RUN apk add make automake gcc g++ subversion python3-dev
RUN pip install pystan==2.19.1.1
RUN pip install --upgrade pip && pip install -r requirements.txt