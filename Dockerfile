FROM python:2
ADD . /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt

EXPOSE 5000

CMD export C_FORCE_ROOT=true; python -m celery -A celery_tasks.celery worker --loglevel=info & \
  python application.py
