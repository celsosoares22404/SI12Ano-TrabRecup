import os
import tempfile
import unittest
from datetime import date
from unittest.mock import patch

from app import create_app, db
from app.models import Tarefa


class GestaoTarefasTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "SECRET_KEY": "test-key",
            }
        )
        self.context = self.app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_usa_diretorio_temporario_no_vercel_sem_base_externa(self):
        with tempfile.TemporaryDirectory() as diretorio_temporario:
            with patch.dict(os.environ, {"VERCEL": "1", "DATABASE_URL": ""}):
                with patch("app.tempfile.gettempdir", return_value=diretorio_temporario):
                    app_vercel = create_app()

            caminho_base = os.path.join(diretorio_temporario, "tarefas.db")
            self.assertEqual(
                app_vercel.config["SQLALCHEMY_DATABASE_URI"],
                f"sqlite:///{caminho_base}",
            )
            with app_vercel.app_context():
                db.engine.dispose()
            self.assertTrue(os.path.isfile(caminho_base))

    def test_urls_postgres_usam_driver_psycopg2(self):
        casos = (
            (
                "postgres://db.example/tarefas",
                "postgresql+psycopg2://db.example/tarefas",
            ),
            (
                "postgresql://db.example/tarefas",
                "postgresql+psycopg2://db.example/tarefas",
            ),
        )
        for url, url_esperada in casos:
            with self.subTest(url=url):
                with patch.dict(os.environ, {"DATABASE_URL": url}):
                    with patch.object(db, "create_all"):
                        app_postgres = create_app()

                self.assertEqual(
                    app_postgres.config["SQLALCHEMY_DATABASE_URI"], url_esperada
                )
                with app_postgres.app_context():
                    db.engine.dispose()

    def test_pagina_inicial_mostra_identificacao(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Nome do Aluno", resposta.data)
        self.assertIn(b"Ano Letivo", resposta.data)

    def test_cria_tarefa_e_mostra_os_detalhes(self):
        resposta = self.client.post(
            "/tarefas",
            data={
                "descricao": "Preparar apresentação",
                "data_fim": "2027-05-20",
                "tempo_previsto": "90",
            },
            follow_redirects=True,
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Preparar apresenta", resposta.data)
        self.assertIn(b"90", resposta.data)
        self.assertEqual(Tarefa.query.count(), 1)

    def test_rejeita_tarefa_sem_tempo_valido(self):
        resposta = self.client.post(
            "/tarefas",
            data={
                "descricao": "Tarefa incompleta",
                "data_fim": "2027-05-20",
                "tempo_previsto": "0",
            },
            follow_redirects=True,
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("tempo previsto deve estar entre".encode(), resposta.data)
        self.assertEqual(Tarefa.query.count(), 0)

    def test_pesquisa_filtra_por_estado_e_elimina_tarefa(self):
        tarefa = Tarefa(
            descricao="Estudar Flask",
            data_fim=date(2027, 5, 20),
            tempo_previsto=60,
            estado="em_progresso",
        )
        db.session.add(tarefa)
        db.session.commit()

        resposta = self.client.get("/tarefas?estado=em_progresso&pesquisa=Flask")
        self.assertIn(b"Estudar Flask", resposta.data)

        resposta = self.client.post(
            f"/tarefas/{tarefa.id}/estado",
            data={"estado": "realizada"},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(db.session.get(Tarefa, tarefa.id).estado, "realizada")

        resposta = self.client.post(f"/tarefas/{tarefa.id}/apagar")
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(Tarefa.query.count(), 0)

    def test_edita_detalhes_da_tarefa(self):
        tarefa = Tarefa(
            descricao="Rever apontamentos",
            data_fim=date(2027, 5, 20),
            tempo_previsto=30,
        )
        db.session.add(tarefa)
        db.session.commit()

        resposta = self.client.post(
            f"/tarefas/{tarefa.id}/editar",
            data={
                "descricao": "Rever apontamentos de Flask",
                "data_fim": "2027-05-21",
                "tempo_previsto": "45",
                "estado": "em_progresso",
            },
        )

        self.assertEqual(resposta.status_code, 302)
        tarefa_atualizada = db.session.get(Tarefa, tarefa.id)
        self.assertEqual(tarefa_atualizada.descricao, "Rever apontamentos de Flask")
        self.assertEqual(tarefa_atualizada.estado, "em_progresso")
        self.assertEqual(tarefa_atualizada.tempo_previsto, 45)


if __name__ == "__main__":
    unittest.main()
