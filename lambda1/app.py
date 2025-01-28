import boto3
import requests
import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO

#load the file with links from .yml file
with open('links.yml') as f:
    links = f.read()

#create a list with the links
links = links.split('\n')

#create a dictionary with the links
event = {}
for link in links:
    link = link.strip()
    if link:
        link = link.split(': ')
        event[link[0]] = link[1]

load_dotenv(dotenv_path=os.getcwd() + '/credentials.env')


def lambda_handler(event, context):

    final_df = pd.DataFrame()

    # get kets as list
    vias = list(event.keys())

    for via in vias:
        
        if 'via' in via.lower():
            new_column_value = via.lower().replace('via ', '').strip()
        else:
            new_column_value = via.lower().strip()

        # Faz o download do arquivo CSV
        url = event[via]
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            # return {"error": f"Erro ao baixar o arquivo: {response.status_code}"}
        
        # get content response from Bytes and convert to pandas dataframe
        content = BytesIO(response.content)
        df = pd.read_csv(content, sep=';', encoding='latin1', low_memory=False)
        df['via'] = new_column_value

        final_df = pd.concat([final_df, df], ignore_index=True)

    # final_df to Bytes format to upload to S3
    towrite = BytesIO()
    final_df.to_csv(towrite, sep=';', encoding='latin1', index=False)


   # Inicializa o cliente do S3 com credenciais das variáveis de ambiente
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

    # Salva o arquivo no bucket S3
    full_content = towrite.getvalue()
    file_name = 'data.csv'
    bucket_name = os.getenv('BUCKET_NAME')
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=full_content)

    # Retorna informações para a próxima Lambda
    return {"bucket_name": bucket_name, "file_name": file_name}
