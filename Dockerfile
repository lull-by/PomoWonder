FROM gorialis/discord.py

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["mypy", "/app/src/"]

CMD [ "python", "main.py" ]