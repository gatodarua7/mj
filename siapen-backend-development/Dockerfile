FROM python:3.9.4

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependencias
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
COPY ./componentes /usr/src/app/componentes
RUN pip install -r requirements.txt
# Copia o projeto
COPY . /usr/src/app/
ADD VERSION .

# Gerencia a base de dados
RUN python manage.py migrate

# Cria usuário padrão
RUN python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='meta').exists() or User.objects.create_superuser('meta', 'admin@example.com', 'meta@123')" ; exit 0

# Criar diretorio de imagens
RUN mkdir -p media
RUN cd media
RUN chmod -R +777 *

# Sobe o backend
EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
