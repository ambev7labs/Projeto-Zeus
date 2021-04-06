import os
import json
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from src.treinamento import treinar
from src.predicao import prever

class StaticRoutes:

    @staticmethod
    def home():
        return render_template("index.html")

    @staticmethod
    def treinamento():
        return render_template("treinamento.html")

    @staticmethod
    def upload():
        return render_template("upload.html")


class Routes:

    @staticmethod
    def listarData():
        basePath = os.path.abspath(os.getcwd()).replace("\\", "/")
        arquivos = os.listdir(f"{basePath}/data")
        res = []

        for arquivo in arquivos:
            file = pd.read_excel(f"{basePath}/data/{arquivo}")
            colunas = [c for c in file]
            res.append({
                "caminho": f"{basePath}/data/{arquivo}",
                "colunas": colunas
            })

        return json.dumps({"status": 200, "data": res})

    @staticmethod
    def treinar():
        # Recupera dados da requisição para treinamento
        body = json.loads(request.data)
        path = body["path"]
        varObjetivo = body["varObjetivo"]
        varEntrada = body["varEntrada"]
        splitTreino = body["splitTreino"]
        otimizador = body["otimizador"]
        custo = body["custo"]
        iteracoes = body["iteracoes"]

        # Executa o treinamento
        erroMin, erroMax, erroMedio, erro50, erro75 = treinar(path,
            varObjetivo, varEntrada, splitTreino=splitTreino,
            otimizador=otimizador, custo=custo, iteracoes=iteracoes)
        treino = {
            "erroMin": erroMin,
            "erroMax": erroMax,
            "erroMedio": erroMedio,
            "erro50": erro50,
            "erro75": erro75
        }

        # Registra o treinamento no arquivo de configuração
        basePath = "/".join(path.split("/")[:-2])
        config = {
            "pathDataset": path,
            "basePath": basePath,
            "varEntrada": varEntrada,
            "varObjetivo": varObjetivo,
            "splitTreino": splitTreino,
            "custo": custo,
            "otimizador": otimizador,
            "iteracoes": iteracoes,
            "treino": treino
        }
        
        file = open(f"{basePath}/config/config.json", "w+")
        json.dump(config, file)

        return json.dumps({
            "status": 200,
            "data": treino
        })

    @staticmethod
    def prever():
        # Recupera o corpo da requisição
        body = json.loads(request.data)
        entrada = body["entrada"]
        
        # Executa a previsão
        basePath = os.path.abspath(os.getcwd()).replace("\\", "/")
        consumoPrevisto = prever(basePath, entrada)

        return json.dumps({
            "status": 200,
            "consumoPrevisto": consumoPrevisto
        })

    @staticmethod
    def getConfig():
        basePath = os.path.abspath(os.getcwd()).replace("\\", "/")
        path = f"{basePath}/config/config.json"

        config = {}
        if os.path.isfile(path):
            file = open(f"{basePath}/config/config.json", "r+")
            config = json.load(file)
        
        return json.dumps({ "status": 200, "data": config })

    @staticmethod
    def upload():
        basePath = os.path.abspath(os.getcwd()).replace("\\", "/")
        arquivo = request.files["file"]
        extensoes = ["xlsx", "xls"]

        if arquivo and arquivo.filename.split(".")[1] in extensoes:
            nome = secure_filename(arquivo.filename)
            path = f"{basePath}/data/{nome}"

            arquivo.save(f"{basePath}/data/{nome}")
            return json.dumps({ "status": 200, "data": { "file": nome, "path": path } })
        else:
            return json.dumps({ "status": 500, "data": { "log": "Arquivo inválido." } })


class Init:

    _app = None

    @classmethod
    def app(cls) -> Flask:
        if cls._app is None:
            cls._app = Flask(__name__)

        return cls._app