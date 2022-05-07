FROM python:3.10

WORKDIR /prj

RUN apt update -y
RUN apt install tmux vim -y # Very useful for debugging

# Fix Locale
# RUN apt install locales -y
# RUN sed -i 's/# en_US/en_US/g' /etc/locale.gen
# RUN locale-gen
# ENV LANG="en_US.utf8"

RUN pip install pipenv

ADD Pipfile .
ADD Pipfile.lock .

RUN pipenv install

ADD . .

ADD sa.json .
ADD drive.json .
ADD telegram.json .

CMD bash
