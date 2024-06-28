FROM python:3.9-slim

# install python packages
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy all files
COPY . .

# set timezone
RUN apt-get update && apt-get install -y tzdata
ENV TZ=Asia/Tokyo

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install cron
RUN apt-get update && apt-get install -y cron

# install vim
RUN apt-get update && apt-get install -y vim

# crontab setting
COPY crontab /etc/cron.d/my-cron-job
RUN chmod 0644 /etc/cron.d/my-cron-job
RUN crontab /etc/cron.d/my-cron-job

# install supervisor
RUN apt-get update && apt-get install -y supervisor

# copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# set workdir
WORKDIR /app

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]