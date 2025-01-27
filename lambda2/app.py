import boto3
import csv
import psycopg2
import os
from datetime import datetime

def lambda_handler(event, context):
    # Informações do S3 recebidas da Lambda 1
    bucket_name = event['bucket_name']
    file_name = event['file_name']

    # Conexão ao S3
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=file_name)
    rows = csv.DictReader(obj['Body'].read().decode('utf-8').splitlines())

    # Filtrar e calcular os dados necessários
    vehicles = ['automovel', 'bicicleta', 'caminhao', 'moto', 'onibus']
    results = []
    for row in rows:
        if row['vehicle'] in vehicles:
            results.append({
                "created_at": datetime.now().isoformat(),
                "road_name": row['road_name'],
                "vehicle": row['vehicle'],
                "number_deaths": int(row['deaths'])
            })

    # Conexão ao banco de dados PostgreSQL em contêiner Docker
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )
    cursor = conn.cursor()

    # Inserir os resultados na tabela do banco de dados
    for result in results:
        cursor.execute("""
            INSERT INTO accidents (created_at, road_name, vehicle, number_deaths)
            VALUES (%s, %s, %s, %s)
        """, (result['created_at'], result['road_name'], result['vehicle'], result['number_deaths']))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Dados processados e salvos com sucesso!", "rows_inserted": len(results)}
