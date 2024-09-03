from flask import Flask, request, redirect, send_file, session, send_from_directory
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, static_folder='.', template_folder='.')
app.secret_key = 'sua_chave_secreta'  # Necessário para usar sessões

# Configuração do banco de dados
DATABASE_URL = 'postgresql://postgres:123456@localhost:5432/postgres'
engine = create_engine(DATABASE_URL)

# Página inicial de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validação simples de login
        if username == '121212' and password == 'password':
            session['logged_in'] = True
            return redirect('/upload')
        else:
            return send_from_directory('.', 'login.html', headers={'X-Status': 'Login falhou. Verifique suas credenciais.'})

    return send_from_directory('.', 'login.html')

# Página de upload (somente acessível após login)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        max_processos = int(request.form.get('max_processos', default=0))  # Número máximo de processos definido pelo usuário

        if not file:
            return "Nenhum arquivo foi enviado."

        try:
            # Lendo o arquivo Excel enviado
            df = pd.read_excel(file)
            required_columns = ['númeroprocesso', 'setoratual', 'localização_caixa', 'datacadastro']

            if not all(col in df.columns for col in required_columns):
                return "Arquivo inválido. Certifique-se de que o arquivo contém as colunas obrigatórias."

            df_filtrado = df[required_columns]

            # Limitar a distribuição ao número escolhido de processos
            if max_processos > 0:
                df_filtrado = df_filtrado.head(max_processos)

            # Consultar o banco de dados para obter processos já distribuídos
            processos_existentes = pd.read_sql('SELECT númeroprocesso FROM processos_distribuidos', engine)
            processos_existentes_set = set(processos_existentes['númeroprocesso'])

            # Filtrar apenas processos que ainda não foram distribuídos
            df_filtrado = df_filtrado[~df_filtrado['númeroprocesso'].isin(processos_existentes_set)]

            # Verificação de quantos processos foram filtrados
            print(f"Processos novos a serem inseridos: {len(df_filtrado)}")

            if df_filtrado.empty:
                return "Todos os processos do arquivo já estão no banco de dados."

            # Selecionando os usuários do banco de dados
            query_usuarios = "SELECT nome FROM usuario"
            usuarios = pd.read_sql(query_usuarios, engine)['nome'].tolist()

            # Distribuindo os responsáveis aleatoriamente de forma justa
            num_processos = len(df_filtrado)
            if num_processos > 0:
                responsaveis = np.tile(usuarios, num_processos // len(usuarios) + 1)[:num_processos]
                np.random.shuffle(responsaveis)
                df_filtrado = df_filtrado.reset_index(drop=True)  # Resetar index para evitar erros ao adicionar nova coluna
                df_filtrado.loc[:, 'responsavel'] = responsaveis  # Criando a coluna 'responsavel'

                # Fazendo um insert separado para cada processo
                for _, row in df_filtrado.iterrows():
                    try:
                        # Inserindo o processo no banco de dados
                        row.to_frame().T.to_sql('processos_distribuidos', engine, if_exists='append', index=False)
                    except IntegrityError:
                        print(f"Processo {row['númeroprocesso']} já existe no banco de dados. Ignorando.")

            # Consultando todos os dados da tabela após a inserção
            df_final = pd.read_sql('SELECT * FROM processos_distribuidos', engine)

            # Exportando todos os dados para um novo arquivo Excel
            output_path = 'processosdistribuidos_completos.xlsx'
            df_final.to_excel(output_path, index=False)

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            return f"Erro ao processar o arquivo: {e}"

    return send_from_directory('.', 'upload.html')

# Rota para arquivos estáticos
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
