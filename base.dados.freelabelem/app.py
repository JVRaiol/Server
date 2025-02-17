from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from pyngrok import ngrok

app = Flask(__name__)

# Caminho para o banco de dados
db_path = 'sqlite:///C:/BD/dados_pessoas.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definindo o modelo para o banco de dados
class Pessoa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    hora_disponivel = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    imagem = db.Column(db.String(200), nullable=True)

# Verificar e criar o banco de dados e as tabelas
def criar_banco_de_dados():
    with app.app_context():
        if not os.path.exists("dados_pessoas.db"):
            print("Banco de dados não encontrado. Criando banco de dados e tabelas...")
            db.create_all()
        else:
            print("Banco de dados já existe.")

# Chamar a função para criar o banco
criar_banco_de_dados()

def salvar_dados(nome, idade, especialidade, hora, description, caminho_imagem):
    """Salva os dados no banco de dados e insere a imagem corretamente."""
    pessoa = Pessoa(nome=nome, idade=idade, especialidade=especialidade,
                    hora_disponivel=hora, descricao=description, imagem=caminho_imagem)
    try:
        db.session.add(pessoa)
        db.session.commit()
        print("Dados salvos com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar dados no banco de dados: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        caminho_imagem = ''
        if 'file' in request.files:
            arquivo = request.files['file']
            if arquivo.filename:
                # Criar o diretório C://BD se não existir
                if not os.path.exists('C://BD'):
                    os.makedirs('C://BD')
                
                nome_arquivo = f"{request.form.get('nome_completo', '').replace(' ', '_')}_{arquivo.filename}"
                caminho_imagem = os.path.join('C://BD/pictures', nome_arquivo)
                print(f"\nSalvando arquivo em: {caminho_imagem}")
                try:
                    arquivo.save(caminho_imagem)
                    print("Arquivo salvo com sucesso!")
                except Exception as e:
                    print(f"Erro ao salvar o arquivo: {e}")

        # Processar os dados do formulário
        nome_completo = request.form.get('nome_completo', '')
        idade = request.form.get('idade', '')
        especialidade = request.form.get('especialidade', '')
        hora_disponivel = request.form.get('hora_disponivel', '')
        description = request.form.get('description', '') 

        print(f'\nNome: {nome_completo}, Idade: {idade}, Especialidade: {especialidade}, Hora: {hora_disponivel}, Descrição: {description}, Imagem: {caminho_imagem}')

        # Salvar os dados no banco de dados
        salvar_dados(nome_completo, idade, especialidade, hora_disponivel, description, caminho_imagem)

        return jsonify({'success': True})

    return render_template('index.html')

if __name__ == '__main__':
    public_url = ngrok.connect(5000).public_url
    print(f' * Ngrok URL: {public_url}')

    app.run(port=5000)
