from routes import Init, StaticRoutes, Routes

app = Init.app()

@app.route("/", methods=["GET"])
def home():
    return StaticRoutes.home()


@app.route("/treinamento", methods=["GET"])
def treinamento():
    return StaticRoutes.treinamento()


@app.route("/upload", methods=["GET"])
def upload():
    return StaticRoutes.upload()


@app.route("/arquivos", methods=["GET"])
def arquivos():
    return Routes.listarData()


@app.route("/treinar", methods=["POST"])
def treinar():
    return Routes.treinar()


@app.route("/config", methods=["GET"])
def config():
    return Routes.getConfig()


@app.route("/prever", methods=["POST"])
def prever():
    return Routes.prever()


@app.route("/arquivo", methods=["POST"])
def salvarArquivo():
    return Routes.upload()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=False)