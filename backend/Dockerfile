FROM python:3.8-slim

COPY . /mousse/
WORKDIR /mousse

# Debugging
# RUN apt-get update && apt-get install -y vim procps

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN chmod +x mousse/main.py
ENTRYPOINT [ "python3", "mousse/main.py" ]
