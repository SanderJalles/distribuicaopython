import pandas as pd

def testar_arquivo_csv(caminho_arquivo):
    try:
        try:
            # Tente ler o arquivo CSV, ignorando linhas problemáticas
            df = pd.read_csv(caminho_arquivo, delimiter=',', encoding='utf-8', on_bad_lines='skip')
            print("Arquivo lido com sucesso com codificação UTF-8.")
        except UnicodeDecodeError:
            # Se falhar, tente com outra codificação
            df = pd.read_csv(caminho_arquivo, delimiter=',', encoding='ISO-8859-1', on_bad_lines='skip')
            print("Arquivo lido com codificação ISO-8859-1.")
        except pd.errors.EmptyDataError:
            print("Erro: O arquivo está vazio.")
            return
        except pd.errors.ParserError as e:
            print(f"Erro de análise: {e}")
            return
        except Exception as e:
            print(f"Erro ao processar o arquivo: {e}")
            return

        if df.empty:
            print("O arquivo está vazio ou não contém dados válidos.")
            return

        print("Colunas no DataFrame:", df.columns)
        print("Dados do DataFrame:")
        print(df.head())

    except Exception as e:
        print(f"Erro inesperado: {e}")

# Substitua pelo caminho correto do seu arquivo CSV
caminho_arquivo = r'C:\Users\Sanderlan\Desktop\Novo(a) Planilha do Microsoft Excel.csv'
testar_arquivo_csv(caminho_arquivo)
