import json
import csv

# Funções de Extração
def carregar_dados_csv(caminho_arquivo):
    """
    Carrega dados de um arquivo CSV e retorna uma lista de dicionários.
    """
    with open(caminho_arquivo, mode='r', newline='', encoding='utf-8') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        return list(leitor_csv)

# Funções de Carga
def salvar_arquivo_csv(dados, caminho_arquivo, campos):
    """
    Salva os dados em um arquivo CSV com cabeçalhos.
    """
    with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
        escritor_csv.writeheader()
        for linha in dados:
            linha_filtrada = {campo: linha[campo] for campo in campos if campo in linha}
            escritor_csv.writerow(linha_filtrada)

# Funções de Transformação
def verificar_finalidade(finalidade_consulta, dados_finalidade, campo_finalidade):
    """
    Verifica se a finalidade da consulta é compatível com a finalidade do dataset.
    """
    for linha in dados_finalidade:
        if finalidade_consulta == linha.get(campo_finalidade):
            print("Finalidade de consulta compatível com a finalidade do dataset.")
            return True
    print("Finalidade de consulta não compatível com a finalidade do dataset.")
    return False

def verificar_contrato_ativo(dados_contrato, campo_status):
    """
    Verifica se há contrato ativo.
    """
    for contrato in dados_contrato:
        if contrato[campo_status].lower() == 'true':
            print("Contrato ativo encontrado.")
            return True
    print("Não há contrato ativo para este acesso.")
    return False

def verificar_consentimento(dados_consentimento, campo_cpf, campo_consent_level, campo_consent_info):
    """
    Verifica o consentimento na tabela de consentimento.
    """
    campos_parciais = {}
    campos_completos = {}

    for consentimento in dados_consentimento:
        cpf = consentimento[campo_cpf]
        consent_level = consentimento[campo_consent_level].lower()
        consent_info = consentimento[campo_consent_info].split(", ")

        if consent_level == "parcial":
            campos_parciais[cpf] = consent_info
        elif consent_level == "completo":
            campos_completos[cpf] = consent_info

    print("Campos parciais permitidos:")
    print(campos_parciais)
    print("Campos completos permitidos:")
    print(campos_completos)

    return campos_parciais, campos_completos

def executar_consulta(dados, campos_permitidos_parciais, campos_permitidos_completos):
    """
    Filtra os campos de acordo com os campos permitidos.
    """
    dados_filtrados = []

    for dado in dados:
        campo_identificacao = parametros["campo_identificacao"]
        identificacao = dado[campo_identificacao]
        dados_permitidos = {}

        if identificacao in campos_permitidos_parciais:
            for campo in campos_permitidos_parciais[identificacao]:
                for c in campo.split(','):
                    if c in dado:
                        dados_permitidos[c] = dado[c]

        if identificacao in campos_permitidos_completos:
            for campo in campos_permitidos_completos[identificacao]:
                for c in campo.split(','):
                    if c in dado:
                        dados_permitidos[c] = dado[c]

        dados_filtrados.append(dados_permitidos)

    return dados_filtrados

# Carregar parâmetros do arquivo JSON
with open('parametros.json') as json_file:
    parametros = json.load(json_file)

# Extração de dados dos arquivos CSV
dados_finalidade = carregar_dados_csv(parametros["caminho_arquivo_finalidade"])
caminho_arquivo_dados = carregar_dados_csv(parametros["caminho_arquivo_dados"])
dados_contrato = carregar_dados_csv(parametros["caminho_arquivo_contrato"])
dados_consentimento = carregar_dados_csv(parametros["caminho_arquivo_consentimento"])

# Definir campos de cabeçalho
campos_cabecalho = caminho_arquivo_dados[0].keys()

# Transformação e Carga
if verificar_finalidade(parametros["finalidade_consulta"], dados_finalidade, parametros["campo_finalidade"]):
    # Carga
    salvar_arquivo_csv(caminho_arquivo_dados, parametros["caminho_arquivo_dados_novo"], campos_cabecalho)
else:
    if verificar_contrato_ativo(dados_contrato, parametros["campo_status"]):
        # Carga
        salvar_arquivo_csv(caminho_arquivo_dados, parametros["caminho_arquivo_dados_novo"], campos_cabecalho)
    else:
        # Transformação
        campos_permitidos_parciais, campos_permitidos_completos = verificar_consentimento(
            dados_consentimento, parametros["campo_cpf"], parametros["campo_consent_level"], parametros["campo_consent_info"])
        dados_filtrados = executar_consulta(caminho_arquivo_dados, campos_permitidos_parciais, campos_permitidos_completos)
        # Carga
        salvar_arquivo_csv(dados_filtrados, parametros["caminho_arquivo_dados_novo"], campos_cabecalho)
