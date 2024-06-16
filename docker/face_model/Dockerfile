FROM python3:10-slim

WORKDIR /app

COPY --chmod=0755 --chown=0:0 face_model/* /app
COPY --chmod=0755 --chown=0:0 requirements.txt /app

RUN python -m venv venv

ENV PATH="/app/venv/bin:$PATH"

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]