FROM python:3.8-slim

WORKDIR /mousse

# Debugging
# RUN apt-get update && apt-get install -y vim procps

RUN apt-get update && apt-get install -y \
    bzip2 \
    wget \
    libxtst6 \
    packagekit-gtk3-module \
    libx11-xcb-dev \
    libdbus-glib-1-2 \
    libxt6 \
    libpci-dev \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Firefox
RUN mkdir -p /usr/local/lib/firefox
RUN wget --no-verbose "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US" -O /tmp/firefox.tar.bz2
RUN tar -xjf /tmp/firefox.tar.bz2 -C /usr/local/lib
RUN ln -s /usr/local/lib/firefox/firefox /usr/local/bin/firefox
# geckodriver
ARG GK_VERSION="0.34.0"
RUN wget --no-verbose -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v$GK_VERSION/geckodriver-v$GK_VERSION-linux64.tar.gz"
RUN tar -C /opt -zxf /tmp/geckodriver.tar.gz
RUN rm /tmp/geckodriver.tar.gz
RUN mv /opt/geckodriver /opt/geckodriver-$GK_VERSION
RUN chmod 755 /opt/geckodriver-$GK_VERSION
RUN ln -fs /opt/geckodriver-$GK_VERSION /usr/bin/geckodriver

# RUN apt-get update && apt-get install -y software-properties-common
# RUN add-apt-repository ppa:mozillateam/ppa
# RUN apt-get update && apt-get install -y --no-install-recommends firefox

RUN pip3 install --upgrade pip

COPY requirements.txt /mousse/
RUN pip3 install -r requirements.txt

COPY . /mousse/
RUN pip3 install .

RUN chmod +x mousse/main.py
ENTRYPOINT [ "python3", "mousse/main.py" ]
