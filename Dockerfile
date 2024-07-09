# Use uma imagem base que já tenha o Chrome e o Selenium
FROM selenium/standalone-chrome

# Instale Python e pip
USER root
RUN apt-get update && apt-get install -y python3 python3-pip \
    && apt-get install -y --no-install-recommends 

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie os arquivos de requisitos para o contêiner
COPY requirements.txt .

# Instale as dependências necessárias
RUN pip3 install --no-cache-dir -r requirements.txt

# Copie o código-fonte para o contêiner
COPY src/ .

# Defina variáveis de ambiente
ENV APIKEY=564c755e-d24f-41c3-9532-eccd8e061469
ENV WEBHOOK=http://localhost:5000/webhook

# Exponha a porta que o Flask usa
EXPOSE 5000

# Comando para executar seu script de automação
CMD ["python3", "app.py"]
