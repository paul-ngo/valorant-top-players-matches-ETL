FROM public.ecr.aws/lambda/python:3.8
# WORKDIR /app
COPY install-browsers.sh requirements.txt config.ini redshift.creds connectRedshift.py valTopPlayersScraperLibs.py valTopPlayersScraperScript.py ./

RUN yum install xz atk cups-libs gtk3 libXcomposite alsa-lib tar \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel unzip bzip2 -y -q

# Install Browsers
RUN /usr/bin/bash install-browsers.sh

# install python libraries
RUN pip install -r requirements.txt -q

# Remove not needed packages
RUN yum remove xz tar unzip bzip2 -y

CMD ["valTopPlayersScraperScript.handler"]