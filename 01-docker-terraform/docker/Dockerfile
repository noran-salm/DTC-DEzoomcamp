FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install pandas pyarrow
COPY . .
CMD ["python", "analyze.py"]
ENTRYPOINT ["bash"]