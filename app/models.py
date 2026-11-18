from datetime import datetime

from app import db


class Tarefa(db.Model):
    __tablename__ = "tarefas"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(500), nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    tempo_previsto = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="nao_iniciada")
    prioridade = db.Column(db.String(10), nullable=False, default="media")
    categoria = db.Column(db.String(60), nullable=False, default="Geral")
    criada_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Tarefa {self.id}: {self.descricao}>"
