import boto3
import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from sqlalchemy import create_engine

load_dotenv(dotenv_path=os.getcwd() + '/credentials.env')
# event = {'bucket_name': os.getenv('BUCKET_NAME'), 'file_name': 'data.csv'}


def lambda_handler(event, context):
    # Informações do S3 recebidas da Lambda 1
    bucket_name = event['bucket_name']
    file_name = event['file_name']

    # Conexão ao S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    obj = s3.get_object(Bucket=bucket_name, Key=file_name)

    toread = BytesIO(obj['Body'].read())
    df = pd.read_csv(toread, sep=';', encoding='latin1', low_memory=False)

    # Tratamento dos dados para inserção no banco
    output_df = pd.DataFrame(columns=['created_at', 'road_name', 'vehicle', 'number_deaths'])
    df_filtered = df[df['mortos'] > 0]
    number_of_deaths = 0
    
    for index, row in df_filtered.iterrows():
        if row['automovel'] > 0 or row['bicicleta'] > 0 or row['caminhao'] > 0 or row['moto'] > 0 or row['onibus'] > 0:
            number_of_deaths += row['mortos']

        vehicles_involved = ''
        if row['automovel'] > 0:
            vehicles_involved += 'automovel,'
        if row['bicicleta'] > 0:
            vehicles_involved += 'bicicleta,'
        if row['caminhao'] > 0:
            vehicles_involved += 'caminhao,'
        if row['moto'] > 0:
            vehicles_involved += 'moto,'
        if row['onibus'] > 0:
            vehicles_involved += 'onibus,'
        vehicles_involved = vehicles_involved[:-1]

        row_info = {
            'created_at': pd.to_datetime(row['data'] + ' ' + row['horario'], format='%d/%m/%Y %H:%M:%S'),
            'road_name': row['via'],
            'vehicle': vehicles_involved,
            'number_deaths': row['mortos']
        }

        output_row = pd.DataFrame(row_info, index=[0])
        output_df = pd.concat([output_df, output_row], ignore_index=True)
    
    to_show = (f'Total de {number_of_deaths} mortes envolvendo os seguintes veículos: automovel, bicicleta, caminhao, moto e onibus.
          nas vias: {output_df["road_name"].unique()}')

    # Conexão ao banco de dados PostgreSQL em contêiner Docker local e inserção de dados no banco
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    output_df.to_sql('fatal_accidents', engine, if_exists='replace', index=False)

    return {"message": "Dados processados e salvos com sucesso!", "Informação geral": to_show}
