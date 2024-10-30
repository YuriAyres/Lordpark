from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração da URI de conexão com o banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/carros_estacionamento'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Carro(db.Model):
    __tablename__ = 'carros'
    carro_id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Text, nullable=True)
    reserva = db.Column(db.Text, nullable=True)

@app.route('/reservar', methods=['POST'])
def reservar_carro():
    dados = request.json
    carro = Carro.query.filter_by(placa=dados['placa']).first()
    if carro:
        carro.reserva = dados['reserva']
    db.session.commit()

@app.route('/estacionar', methods=['POST'])
def carro_estacionar():
    dados = request.json
    carro_id = dados.get('carro_id')
    
    carro = Carro.query.get(carro_id)
    
    if carro:
        if carro.status == 'estacionado':
            return jsonify({"message": "Carro já está estacionado!"}), 400
        carro.status = 'estacionado'  # Atualiza o status para 'estacionado'
    db.session.commit()

@app.route('/sair', methods=['POST'])
def carro_sair():
    dados = request.json
    carro_id = dados.get('carro_id')
    
    carro = Carro.query.get(carro_id)
    
    if carro:
        if carro.status == 'estacionado':
            carro.status = ''  # Atualiza o status para vazio
            carro.reserva = '' # Atualiza a reserva para vazia
        else:
            return jsonify({"message": "Carro não registrou entrada!"}), 400
    db.session.commit()

@app.route('/carros', methods=['GET'])
def get_carros():
    # Faz a consulta para obter todos os carros do banco de dados
    carros = Carro.query.all()

    # Transforma o resultado da consulta em um formato JSON
    carros_list = [{'placa': carro.placa, 'nome': carro.nome, 'status': carro.status, 'reserva': carro.reserva} for carro in carros]
    return jsonify(carros_list), 200

@app.route('/carros/<tag>', methods=['GET'])
def get_carro(tag):
    carro = Carro.query.filter_by(carro_id=tag).first()
    if carro is None:
        return jsonify({"message": "Carro não encontrado."}), 404
    return jsonify({"placa": carro.placa, "nome": carro.nome, "Status": carro.status, "reserva": carro.reserva}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


