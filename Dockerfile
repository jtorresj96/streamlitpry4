# Utiliza una imagen base con Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de la aplicación Streamlit a la imagen
COPY streamlit_app.py .

# Instala las dependencias necesarias
RUN pip install streamlit requests

# Exponer el puerto de Streamlit
EXPOSE 8506

# Define el comando para ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8506", "--server.address=0.0.0.0"]