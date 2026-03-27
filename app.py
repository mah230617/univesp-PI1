from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_visual_producoes'

# Configuração do Banco de Dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cpf = db.Column(db.String(18), unique=True, nullable=False)
    data_nascimento = db.Column(db.String(10))
    telefone = db.Column(db.String(20))
    cep = db.Column(db.String(9))
    logradouro = db.Column(db.String(100))
    bairro = db.Column(db.String(50))
    cidade = db.Column(db.String(50))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(50))

# --- FUNÇÃO DE BACKUP EM TXT ---
def gerar_backup_txt():
    clientes = Cliente.query.all()
    try:
        with open('backup_clientes.txt', 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE CLIENTES - VISUAL PRODUÇÕES\n")
            f.write("="*45 + "\n")
            for c in clientes:
                f.write(f"NOME/RAZÃO SOCIAL: {c.nome}\n")
                f.write(f"CPF: {c.cpf} | NASC: {c.data_nascimento}\n")
                f.write(f"ENDEREÇO: {c.logradouro}, {c.numero} ({c.complemento or 'S/C'}) - {c.bairro}, {c.cidade}\n")
                f.write(f"CONTATO: {c.telefone} | {c.email}\n")
                f.write("-" * 25 + "\n")
    except Exception as e:
        print(f"Erro ao gerar backup: {e}")

# --- ROTAS DO SISTEMA ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def auth():
    user = request.form.get('username')
    pw = request.form.get('password')
    usuario = Usuario.query.filter_by(username=user, password=pw).first()
    if usuario:
        session['username'] = user
        return redirect(url_for('index'))
    flash('Usuário ou senha inválidos!')
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    clientes = Cliente.query.all()
    return render_template('index.html', clientes=clientes)

@app.route('/add', methods=['POST'])
def add_cliente():
    if 'username' not in session: return redirect(url_for('login'))
    
    try:
        novo = Cliente(
            nome=request.form.get('nome'),
            email=request.form.get('email'),
            cpf=request.form.get('cpf'),
            data_nascimento=request.form.get('data_nascimento'),
            telefone=request.form.get('telefone'),
            cep=request.form.get('cep'),
            logradouro=request.form.get('logradouro'),
            bairro=request.form.get('bairro'),
            cidade=request.form.get('cidade'),
            numero=request.form.get('numero'),
            complemento=request.form.get('complemento')
        )
        db.session.add(novo)
        db.session.commit()
        gerar_backup_txt()
        flash('Cliente cadastrado com sucesso!')
    except:
        db.session.rollback()
        flash('Erro: CPF ou E-mail já cadastrados no sistema.')
        
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'username' not in session: return redirect(url_for('login'))
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente.nome = request.form.get('nome')
        cliente.email = request.form.get('email')
        cliente.cpf = request.form.get('cpf')
        cliente.data_nascimento = request.form.get('data_nascimento')
        cliente.telefone = request.form.get('telefone')
        cliente.cep = request.form.get('cep')
        cliente.logradouro = request.form.get('logradouro')
        cliente.bairro = request.form.get('bairro')
        cliente.cidade = request.form.get('cidade')
        cliente.numero = request.form.get('numero')
        cliente.complemento = request.form.get('complemento')
        
        db.session.commit()
        gerar_backup_txt()
        flash('Dados atualizados com sucesso!')
        return redirect(url_for('index'))
    
    return render_template('edit.html', cliente=cliente)

@app.route('/delete/<int:id>')
def delete(id):
    if 'username' not in session: return redirect(url_for('login'))
    cliente = Cliente.query.get(id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        gerar_backup_txt()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Garante o acesso inicial para Maíra, Luiz e Sabrina
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', password='123')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)