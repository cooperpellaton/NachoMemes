import io
import json

from flask import Flask, jsonify, request, send_file, send_from_directory, render_template
from flask_cors import CORS

from nachomemes import Configuration
from nachomemes.store import Store, update_serialization, TemplateEncoder


def make_server(store: Store) -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def root_path():
        return "NachoMemes REST Endpoint"

    @app.route("/api/<guild_id>/memes")
    def list_memes(guild_id):
        return jsonify(update_serialization(store.list_memes(guild_id)))

    @app.route("/api/<guild_id>/memes-name")
    def list_of_meme_names(guild_id):
        data = store.list_memes(guild_id)
        list_names = []
        for entry in data:
            list_names.append(entry['name'])
        return json.dumps(list_names, cls=TemplateEncoder)

    @app.route("/api/<guild_id>/memes/<template_id>")
    def get_template_data(guild_id: str, template_id: str):
        data = store.get_template_data(guild_id, template_id)
        return json.dumps(data, cls=TemplateEncoder)

    @app.route("/api/<guild_id>/memes/<template_id>/render")
    def render(guild_id: str, template_id: str):
        meme = store.get_template(guild_id, template_id)
        text = "\n".join(request.args.getlist("text"))
        print(text)
        buffer = io.BytesIO()
        meme.render(text, buffer)
        buffer.seek(0)
        return send_file(buffer, mimetype="image/png")  # type: ignore

    @app.route('/api/<guild_id>/memes/<template_id>/render')
    def baseimage(guild_id: str, template_id: str):
        meme = store.get_template(guild_id, template_id)
        text = " ".join(request.args.getlist('text'))
        print(text)
        buffer = io.BytesIO()
        meme.render(text, buffer)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='image/png')

    @app.route('/api/<guild_id>/save-template/<template_id>', methods=['GET', 'POST'])
    def save_template(guild_id: str, template_id: str):
        print("Updated: " + template_id + " in guild: " + guild_id)
        return store.save_meme(guild_id, request.json)
    
    @app.route('/update-template/<path:filename>')
    def download_file(filename: str):
        folder_path = "../frontend-templating"
        return send_from_directory(folder_path, filename)
    
    @app.route('/edit/<guild_id>/update-template/<template_id>')
    def update_temp(guild_id, template_id):
        return render_template('update_meme.html', guild_id = guild_id, template_id = template_id)

    @app.route('/edit/<guild_id>')
    def main_render(guild_id):
        return render_template('main.html', guild_id = guild_id)

    @app.route('/edit/<guild_id>/memes')
    def memes(guild_id):
        return render_template('list_memes.html', guild_id = guild_id)

    @app.route('/build/<guild_id>/new')
    def new_meme(guild_id):
        return render_template('new_meme.html', guild_id = guild_id)

    return app


if __name__ == "__main__":
    config = Configuration()
    app = make_server(config.store)
    app.debug = config.debug
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.run()
