from system import create_app
# @app.get("/<path:path>")
# def send_file(path):
#     return send_file(path)

app = create_app()
app.app_context().push()
app.run(debug=True,host="0.0.0.0")