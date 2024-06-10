from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd
from django.http import JsonResponse

df = None

def index(request):
    return render(request, 'uploaddoc/navbar.html')

def upload_excel(request):
    global df

    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']

        read_functions = {
            'xlsx': pd.read_excel,
            'xls': pd.read_excel,
            'csv': pd.read_csv,
            # Add more extensions as needed
        }

        file_extension = file.name.split('.')[-1].lower()

        if file_extension in read_functions:
            df = read_functions[file_extension](file)

            # Remove newline characters in text columns
            for coluna in df.select_dtypes(include='object').columns:
                df[coluna] = df[coluna].str.replace('\n', '')

            colunas = df.columns.tolist()

            return render(request, 'uploaddoc/preview.html', {'data': df.to_html(classes='table table-bordered table-striped', index=False), 'colunas': colunas})
        else:
            return HttpResponse('Unsupported file format. Please upload a supported format.')

    return render(request, 'uploaddoc/upload_excel.html')

def salvar_dados(request):
    global df

    if request.method == 'POST' and df is not None:
        campos_selecionados = request.POST.get('colunas_selecionadas').split(',')

        # Logic to process selected fields (filter the DataFrame)
        df_filtrado = df[campos_selecionados].copy().reset_index(drop=True)

        # Remove duplicate columns, if any
        df_filtrado = df_filtrado.loc[:, ~df_filtrado.columns.duplicated()]

        # Remove newline characters in text columns
        for coluna in df_filtrado.select_dtypes(include='object').columns:
            df_filtrado[coluna] = df_filtrado[coluna].str.replace('\n', '')

        # Convert the filtered DataFrame to HTML, including the header
        tabela_html = df_filtrado.to_html(index=False, classes='table table-bordered table-striped', justify='center')

        return render(request, 'uploaddoc/salvar_dados.html', {'tabela_html': tabela_html, 'colunas': campos_selecionados})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def gerar_relatorios_municipios(request):
    if request.method == 'GET' and df is not None:
        municipios = df['MUNICÍPIO'].unique()

        # Convert to uppercase and sort alphabetically
        municipios = sorted(municipios)

        return render(request, 'uploaddoc/selecionar_municipio.html', {'municipios': municipios})
    else:
        return HttpResponse('Upload a file first.')

def relatorio_individual(request):
    global df

    if request.method == 'POST' and df is not None:
        municipio_selecionado = request.POST.get('municipio')
        df_municipio = df[df['MUNICÍPIO'] == municipio_selecionado]

        # Check if there is at least one row for the selected municipality
        if not df_municipio.empty:
            # Get data from the first row of the DataFrame
            dados = df_municipio.iloc[0].to_dict()

            # Specific fields to exclude
            campos_excluir = ['ID', 'DATA DE ENVIO', 'ÚLTIMA PÁGINA', 'IDIOMA INICIAL', 'SEMENTE', ']', '].1', '].3', '].4', ]

            # Exclude "nan" values and specific fields
            dados_filtrados = {campo: valor for campo, valor in dados.items() if campo not in campos_excluir and not pd.isna(valor)}

            # Render the template normally for display on the web page
            return render(request, 'uploaddoc/relatorio_individual.html', {'dados': dados_filtrados, 'municipio': municipio_selecionado})

        else:
            return HttpResponse('Município não encontrado no DataFrame.')
    else:
        return HttpResponse('Method not allowed or upload a file first.')


def relatorio_geral(request):
    global df  # Certifique-se de que df esteja globalmente definido

    # Verificar se o DataFrame está carregado
    if df is not None and not df.empty:
        # Criar uma lista para armazenar os dados de todas as linhas
        dados_filtrados = []

        # Criar um conjunto para armazenar perguntas únicas
        perguntas_unicas = set()

        # Iterar sobre as linhas do DataFrame
        for _, row in df.iterrows():
            # Obter dados da linha
            dados = row.to_dict()

            # Campos específicos a serem excluídos
            campos_excluir = ['ID', 'DATA DE ENVIO', 'ÚLTIMA PÁGINA', 'IDIOMA INICIAL', 'SEMENTE', ']', '].1', '].3', '].4']

            # Excluir "nan" values e campos específicos
            dados_filtrados_row = {campo: valor for campo, valor in dados.items() if campo not in campos_excluir and not pd.isna(valor)}

            dados_filtrados.append(dados_filtrados_row)

            # Adicionar perguntas ao conjunto de perguntas únicasf
            for pergunta in dados_filtrados_row.keys():
                perguntas_unicas.add(pergunta)

        # Ordenar os municípios em ordem alfabética
        dados_filtrados = sorted(dados_filtrados, key=lambda x: x.get('MUNICÍPIO', ''))  # Substitua 'nome_municipio' pelo campo real

        # Renderizar o template normalmente para exibição na página web
        return render(request, 'uploaddoc/relatorio_geral.html', {'dados': dados_filtrados, 'perguntas_unicas': perguntas_unicas})
    else:
        return HttpResponse('DataFrame não carregado ou vazio. Faça o upload de um arquivo primeiro ou verifique se há dados no arquivo.')