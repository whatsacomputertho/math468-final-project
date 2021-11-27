FROM python:3.10
ADD ./requirements.txt /back-end/requirements.txt
WORKDIR /back-end
RUN pip install -r requirements.txt
ADD . /back-end
ENTRYPOINT ["python"]
CMD ["/back-end/main.py"]
EXPOSE 3000