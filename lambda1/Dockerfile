# Usando a imagem oficial da AWS Lambda para Python
FROM public.ecr.aws/lambda/python:3.8

# Copiar o código da Lambda 1
COPY app.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

# Instalar dependências
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Definir o handler (nome do arquivo e função principal)
CMD ["app.handler"]