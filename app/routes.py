from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import Tarefa

bp = Blueprint("tarefas", __name__)

ESTADOS = {
    "nao_iniciada": "Não iniciada",
    "em_progresso": "Em progresso",
    "realizada": "Realizada",
}
PRIORIDADES = {"baixa": "Baixa", "media": "Média", "alta": "Alta"}


def _ler_formulario():
    descricao = request.form.get("descricao", "").strip()
    categoria = request.form.get("categoria", "Geral").strip() or "Geral"
    estado = request.form.get("estado", "nao_iniciada")
    prioridade = request.form.get("prioridade", "media")

    if not descricao:
        return None, "A descrição da tarefa é obrigatória."
    if len(descricao) > 500:
        return None, "A descrição não pode ultrapassar 500 caracteres."
    if len(categoria) > 60:
        return None, "A categoria não pode ultrapassar 60 caracteres."

    try:
        data_fim = date.fromisoformat(request.form.get("data_fim", ""))
    except ValueError:
        return None, "Indica uma data de fim válida."

    try:
        tempo_previsto = int(request.form.get("tempo_previsto", ""))
    except ValueError:
        return None, "Indica o tempo previsto em minutos."
    if not 1 <= tempo_previsto <= 6000:
        return None, "O tempo previsto deve estar entre 1 e 6000 minutos."
    if estado not in ESTADOS:
        return None, "Seleciona um estado válido."
    if prioridade not in PRIORIDADES:
        return None, "Seleciona uma prioridade válida."

    return {
        "descricao": descricao,
        "categoria": categoria,
        "data_fim": data_fim,
        "tempo_previsto": tempo_previsto,
        "estado": estado,
        "prioridade": prioridade,
    }, None


@bp.app_context_processor
def disponibilizar_opcoes():
    return {"estados": ESTADOS, "prioridades": PRIORIDADES}


@bp.route("/")
def inicio():
    return render_template("index.html")


@bp.route("/tarefas", methods=["GET", "POST"])
def lista():
    if request.method == "POST":
        dados, erro = _ler_formulario()
        if erro:
            flash(erro, "erro")
        else:
            db.session.add(Tarefa(**dados))
            db.session.commit()
            flash("Tarefa adicionada com sucesso.", "sucesso")
        return redirect(url_for("tarefas.lista"))

    estado = request.args.get("estado", "")
    pesquisa = request.args.get("pesquisa", "").strip()
    consulta = Tarefa.query

    if estado in ESTADOS:
        consulta = consulta.filter_by(estado=estado)
    if pesquisa:
        consulta = consulta.filter(Tarefa.descricao.ilike(f"%{pesquisa}%"))

    tarefas = consulta.order_by(Tarefa.data_fim.asc(), Tarefa.id.desc()).all()
    return render_template("tarefas.html", tarefas=tarefas)


@bp.route("/tarefas/<int:tarefa_id>/editar", methods=["GET", "POST"])
def editar(tarefa_id):
    tarefa = db.get_or_404(Tarefa, tarefa_id)
    if request.method == "POST":
        dados, erro = _ler_formulario()
        if erro:
            flash(erro, "erro")
            return redirect(url_for("tarefas.editar", tarefa_id=tarefa.id))

        for campo, valor in dados.items():
            setattr(tarefa, campo, valor)
        db.session.commit()
        flash("Tarefa atualizada com sucesso.", "sucesso")
        return redirect(url_for("tarefas.lista"))

    return render_template("editar.html", tarefa=tarefa)


@bp.route("/tarefas/<int:tarefa_id>/estado", methods=["POST"])
def atualizar_estado(tarefa_id):
    tarefa = db.get_or_404(Tarefa, tarefa_id)
    novo_estado = request.form.get("estado", "")
    if novo_estado not in ESTADOS:
        flash("Seleciona um estado válido.", "erro")
    else:
        tarefa.estado = novo_estado
        db.session.commit()
        flash("Estado da tarefa atualizado.", "sucesso")
    return redirect(url_for("tarefas.lista"))


@bp.route("/tarefas/<int:tarefa_id>/apagar", methods=["POST"])
def apagar(tarefa_id):
    tarefa = db.get_or_404(Tarefa, tarefa_id)
    db.session.delete(tarefa)
    db.session.commit()
    flash("Tarefa eliminada.", "sucesso")
    return redirect(url_for("tarefas.lista"))
