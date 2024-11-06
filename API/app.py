from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração da URI de conexão com o banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/carros_estacionamento'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

sensores_inativos = None

class Carro(db.Model):
    __tablename__ = 'carros'
    carro_id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Text, nullable=True)
    reserva = db.Column(db.Text, nullable=True)
    modelo = db.Column(db.Text, nullable=True)

@app.route('/reservar', methods=['POST'])
def reservar_carro():
    dados = request.json
    carro = Carro.query.filter_by(placa=dados['placa']).first()
    
    if carro:
        if carro.reserva:  # Verifica se já existe uma reserva
            return jsonify({"message": "Carro já está reservado."}), 400
        
        carro.reserva = dados['reserva']
        db.session.commit()
        return jsonify({"message": "Reserva atualizada com sucesso!"}), 200
    else:
        return jsonify({"message": "Carro não encontrado."}), 404

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
    return jsonify({"message": "Entrada registrada com sucesso!"}), 200

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
    return jsonify({"message": "Saída registrada com sucesso!"}), 200

@app.route('/vagas', methods=['POST'])
def vagas_disponiveis():
    global sensores_inativos
    dados = request.json
    sensores_inativos = dados.get('sensores_inativos')
    return jsonify({"message": "Número de sensores inativos atualizado com sucesso!"}), 200
    
@app.route('/vagas', methods=['GET'])
def get_vagas_disponiveis():
    if sensores_inativos is not None:
        return jsonify({"sensores_inativos": sensores_inativos}), 200
    else:
        return jsonify({"message": "Número de sensores inativos ainda não atualizado."}), 404

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

@app.route('/login/<username>', methods=['GET'])
def get_carro(username):
    carro = Carro.query.filter_by(nome=username).first()
    if carro is None:
        return jsonify({"message": "Carro não encontrado."}), 404
    return jsonify({"placa": carro.placa, "modelo": carro.modelo, "Status": carro.status, "reserva": carro.reserva}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


