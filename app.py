from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

from notes import Notes


def create_app(database: Path | None = None) -> Flask:
    app = Flask(__name__)
    notes = Notes(database if database is not None else Path(app.instance_path) / "notes.sqlite3")
    notes.initialize()

    @app.get("/")
    def index():
        query = request.args.get("q", "").strip()
        keyword = query.casefold()
        matches = [note for note in notes.list_all() if keyword in note["title"].casefold()]
        return render_template("index.html", notes=matches, query=query)

    @app.post("/notes")
    def create_note():
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title or not body or len(title) > 100 or len(body) > 5000:
            return render_template(
                "index.html", notes=notes.list_all(), title=title, body=body,
                error="Введите заголовок до 100 символов и текст до 5000 символов.",
            ), 400

        note_id = notes.create(title, body)
        return redirect(url_for("show_note", note_id=note_id), code=303)

    @app.get("/notes/<int:note_id>")
    def show_note(note_id: int):
        note = notes.get(note_id)
        if note is None:
            abort(404)
        return render_template("note.html", note=note)

    return app
