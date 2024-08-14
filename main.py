from flask import Flask, request, redirect, send_file, session, send_from_directory
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

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

        if not file:
            return "Nenhum arquivo foi enviado."

        try:
            # Lendo o arquivo Excel enviado
            df = pd.read_excel(file)
            required_columns = ['númeroprocesso', 'setoratual', 'localização_caixa', 'datacadastro']

            if not all(col in df.columns for col in required_columns):
                return "Arquivo inválido. Certifique-se de que o arquivo contém as colunas obrigatórias."

            df_filtrado = df[required_columns]

            # Buscando todos os usuários da tabela `usuarios`
            query_usuarios = "SELECT nome FROM usuario"
            usuarios = pd.read_sql(query_usuarios, engine)

            # Contando processos já distribuídos por usuário
            query_contagem = "SELECT responsavel, COUNT(*) as count FROM processos_distribuidos GROUP BY responsavel"
            contagem_processos = pd.read_sql(query_contagem, engine)
            contagem_processos = contagem_processos.set_index('responsavel').reindex(usuarios['nome'], fill_value=0).reset_index()

            # Ordenando os usuários pela quantidade de processos atribuídos (ordem crescente)
            usuarios_ordenados = contagem_processos.sort_values(by='count')['responsavel'].tolist()

            # Distribuindo os responsáveis de forma justa e aleatória
            num_processos = len(df_filtrado)
            responsaveis = []
            for i in range(num_processos):
                usuario = usuarios_ordenados[i % len(usuarios_ordenados)]
                responsaveis.append(usuario)

            # Misturando a lista de responsáveis para aleatoriedade
            np.random.shuffle(responsaveis)
            df_filtrado['responsavel'] = responsaveis

            # Salvando os novos dados no banco de dados
            df_filtrado.to_sql('processos_distribuidos', engine, if_exists='append', index=False)

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
