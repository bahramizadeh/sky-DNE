FROM python:3.10
EXPOSE 5010
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["flask", "run", "-p", "5010", "--host", "0.0.0.0"]