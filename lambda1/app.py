import boto3
import requests
import os

def lambda_handler(event, context):
    url = event['csv_url']  # URL do CSV fornecida no evento
    bucket_name = os.getenv('BUCKET_NAME', 'accident-data-bucket')  # Nome do bucket do S3
    file_name = 'data.csv'  # Nome do arquivo no bucket S3

    # Faz o download do arquivo CSV
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": f"Erro ao baixar o arquivo: {response.status_code}"}

    # Salva o arquivo no bucket S3
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=response.content)

    # Retorna informações para a próxima Lambda
    return {"bucket_name": bucket_name, "file_name": file_name}
