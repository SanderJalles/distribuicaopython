from flask import Flask, request, redirect, send_file, session, send_from_directory, jsonify, make_response
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, static_folder='.', template_folder='.')
app.secret_key = 'sua_chave_secreta'

# Configuração do banco de dados
DATABASE_URL = 'postgresql://postgres:123456@localhost:5432/postgres'
engine = create_engine(DATABASE_URL)

# Página inicial de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == '121212' and password == 'password':
            session['logged_in'] = True
            return redirect('/upload')
        else:
            response = make_response(send_from_directory('.', 'login.html'))
            response.headers['X-Status'] = 'Login falhou. Verifique suas credenciais.'
            return response

    return send_from_directory('.', 'login.html')


# Página de upload (somente acessível após login)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        max_processos = int(request.form.get('max_processos', default=0))  # Número máximo de processos definido pelo usuário

        if not file:
            return jsonify({"status": "error", "message": "Nenhum arquivo foi enviado."})

        try:
            # Tente ler o arquivo CSV
            try:
                df = pd.read_csv(file, delimiter=';', encoding='ISO-8859-1')
            except UnicodeDecodeError:
                df = pd.read_csv(file, delimiter=';', encoding='UTF-8')
            except pd.errors.EmptyDataError:
                return jsonify({"status": "error", "message": "O arquivo está vazio."})
            except pd.errors.ParserError:
                return jsonify({"status": "error", "message": "Erro ao analisar o arquivo CSV."})
            except Exception as e:
                return jsonify({"status": "error", "message": f"Erro ao processar o arquivo: {e}"})

            # Verifique se o DataFrame contém dados
            if df.empty:
                return jsonify({"status": "error", "message": "O arquivo está vazio ou não contém dados válidos."})

            # Verificar se as colunas obrigatórias estão presentes
            required_columns = ['Processo', 'Situação', 'SetorDestino']
            if not all(col in df.columns for col in required_columns):
                return jsonify({"status": "error", "message": "Arquivo inválido. Certifique-se de que o arquivo contém as colunas obrigatórias: 'Processo', 'Situação', 'SetorDestino'."})

            # Filtragem e limpeza dos dados
            df_filtrado = df[required_columns].dropna().apply(lambda x: x.str.strip())

            # Filtrar apenas os processos com "Situação" = 'TRAMITACAO' ou 'ANEXADO'
            df_filtrado = df_filtrado[df_filtrado['Situação'].isin(['TRAMITACAO', 'ANEXADO'])]

            # Limitar a distribuição ao número escolhido de processos
            if max_processos > 0:
                df_filtrado = df_filtrado.head(max_processos)

            # Consultar o banco de dados para obter processos já distribuídos
            processos_existentes = pd.read_sql('SELECT "Processo" FROM processos_distribuidos', engine)
            processos_existentes_set = set(processos_existentes['Processo'])

            # Separar os processos duplicados dos novos
            processos_duplicados = df_filtrado[df_filtrado['Processo'].isin(processos_existentes_set)]
            processos_novos = df_filtrado[~df_filtrado['Processo'].isin(processos_existentes_set)]

            # Verificar se há novos processos para serem distribuídos
            if processos_novos.empty:
                return jsonify({"status": "warning", "message": "Todos os processos do arquivo já estão no banco de dados."})

            # Selecionando os usuários do banco de dados
            query_usuarios = "SELECT nome FROM usuario"
            usuarios = pd.read_sql(query_usuarios, engine)['nome'].tolist()

            # Distribuindo os responsáveis aleatoriamente de forma justa
            num_processos = len(processos_novos)
            responsaveis = np.tile(usuarios, num_processos // len(usuarios) + 1)[:num_processos]
            np.random.shuffle(responsaveis)
            processos_novos = processos_novos.reset_index(drop=True)
            processos_novos.loc[:, 'responsavel'] = responsaveis

            # Lista para armazenar processos duplicados
            duplicados = processos_duplicados['Processo'].tolist()

            # Inserir cada processo novo no banco de dados
            for _, row in processos_novos.iterrows():
                try:
                    row.to_frame().T.to_sql('processos_distribuidos', engine, if_exists='append', index=False)
                except IntegrityError:
                    duplicados.append(f"Processo {row['Processo']} já existe no banco de dados.")

            # Verificar se houve processos duplicados
            if duplicados:
                return jsonify({"status": "warning", "message": "Alguns processos já estavam no banco de dados.", "duplicados": duplicados})

            # Consultando todos os dados da tabela após a inserção
            df_final = pd.read_sql('SELECT * FROM processos_distribuidos', engine)

            # Exportando todos os dados para um novo arquivo Excel
            output_path = 'processosdistribuidos_completos.xlsx'
            df_final.to_excel(output_path, index=False)

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            return jsonify({"status": "error", "message": f"Erro ao processar o arquivo: {e}"})

    return send_from_directory('.', 'upload.html')

@app.route('/historico', methods=['GET'])
def historico():
    try:
        # Consultar a tabela de processos distribuídos
        df_historico = pd.read_sql('SELECT * FROM processos_distribuidos ORDER BY "Processo"', engine)
        
        # Converter os dados para uma lista de dicionários
        historico_data = df_historico.to_dict(orient='records')
        
        return jsonify({"status": "success", "data": historico_data})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao consultar o histórico: {e}"})
    
@app.route('/process-file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo foi enviado.'}), 400

    file = request.files['file']
    try:
        # Tente ler o arquivo CSV
        df = pd.read_csv(file, delimiter=';', encoding='ISO-8859-1')
        print("Arquivo lido com sucesso com codificação ISO-8859-1 e delimitador ';'.")

        # Verificar se as colunas obrigatórias estão presentes
        required_columns = [col for col in required_columns if col not in df.columns]
        if required_columns:
            return jsonify({'status': 'error', 'message': f'Colunas faltantes: {", ".join(required_columns)}'}), 400

        # Gera a lista de processos para o checklist
        processos = df['Processo'].tolist()
        return jsonify({'status': 'success', 'processos': processos})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao processar o arquivo: {e}'}), 500

# Rota para distribuir os processos selecionados
@app.route('/distribuir-processos', methods=['POST'])
def distribuir_processos():
    try:
        processos_selecionados = request.json.get('processos')
        if not processos_selecionados:
            return jsonify({'status': 'error', 'message': 'Nenhum processo foi selecionado.'}), 400

        # Consulta os processos já distribuídos
        processos_existentes = pd.read_sql('SELECT "Processo" FROM processos_distribuidos', engine)
        processos_existentes_set = set(processos_existentes['Processo'])

        # Filtra os processos que já existem no banco de dados
        processos_novos = [proc for proc in processos_selecionados if proc not in processos_existentes_set]
        if not processos_novos:
            return jsonify({'status': 'warning', 'message': 'Todos os processos selecionados já foram distribuídos.'})

        # Selecionando os usuários do banco de dados
        query_usuarios = "SELECT nome FROM usuario"
        usuarios = pd.read_sql(query_usuarios, engine)['nome'].tolist()

        # Verificando se há usuários suficientes para distribuir os processos
        if len(usuarios) == 0:
            return jsonify({'status': 'error', 'message': 'Não há usuários disponíveis para distribuição.'}), 400

        num_processos = len(processos_novos)

        # Certificando que todos os usuários receberão pelo menos um processo antes de repetir a distribuição
        responsaveis = np.tile(usuarios, num_processos // len(usuarios) + 1)[:num_processos]
        np.random.shuffle(responsaveis)

        # Preparar os dados para inserção no banco
        data_inserir = pd.DataFrame({
            'Processo': processos_novos,
            'responsavel': responsaveis,
            'Situação': ['TRAMITACAO'] * num_processos,  # Situação padrão
            'SetorDestino': ['Setor X'] * num_processos  # Setor padrão
        })

        # Tratamento de exceção ao inserir processos no banco
        try:
            data_inserir.to_sql('processos_distribuidos', engine, if_exists='append', index=False)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Erro ao inserir dados no banco: {e}'})

        return jsonify({'status': 'success', 'message': 'Processos distribuídos com sucesso.'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao distribuir processos: {e}'}) 

# Rota para arquivos estáticos
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
