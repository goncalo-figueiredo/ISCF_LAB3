# 1. Usar uma imagem base oficial e leve do Python
FROM python:3.12-slim

# 2. Definir a pasta de trabalho dentro do contentor
WORKDIR /app

# 3. Copiar o requirements e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo o teu código para dentro do contentor
COPY . .

# 5. Expor a porta 50051 (a porta onde o gRPC está à escuta)
EXPOSE 50051

# 6. Comando para arrancar o servidor quando o contentor iniciar
CMD ["python", "server.py"]