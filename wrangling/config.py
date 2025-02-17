import os

def get_data_home():
    data_home = os.getenv('DATA_STAGE_HOME','../staging/')
    if (data_home.endswith('/') == False):
        data_home = data_home+'/'

    return data_home

#no caso de atualizar uma base existente, esta é a pasta onde o script (stage02) busca o dataset existente
def get_existing_data_home():
    data_home = os.getenv('EXISTING_DATASET_HOME','../dataset/')
    if (data_home.endswith('/') == False):
        data_home = data_home+'/'

    return data_home

arquivos_to_append = [
        '2023-10-01_Alvaras-Base_de_Dados.CSV', 
        '2023-11-01_Alvaras-Base_de_Dados.CSV', 
        '2023-12-01_Alvaras-Base_de_Dados.CSV', 
        '2024-01-01_Alvaras-Base_de_Dados.CSV', 
        '2024-02-01_Alvaras-Base_de_Dados.CSV', 
        '2024-03-01_Alvaras-Base_de_Dados.CSV', 
        '2024-04-01_Alvaras-Base_de_Dados.CSV', 
        '2024-05-01_Alvaras-Base_de_Dados.CSV', 
        '2024-06-01_Alvaras-Base_de_Dados.CSV', 
        '2024-07-01_Alvaras-Base_de_Dados.CSV', 
        '2024-08-01_Alvaras-Base_de_Dados.CSV', 
        '2024-09-01_Alvaras-Base_de_Dados.CSV', 
        '2024-10-01_Alvaras-Base_de_Dados.CSV', 
        '2024-11-01_Alvaras-Base_de_Dados.CSV',
        '2024-12-01_Alvaras-Base_de_Dados.CSV']