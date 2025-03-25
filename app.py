import io
import os
import xml.sax

from flask import Flask, request, jsonify

from db import *
from xml_handlers import (XMLHandler, AttributeCollectorHandler,
                          TagCounterHandler, validate_xml)

app = Flask(__name__)
app.config.from_object(__name__)
FILE_DIRECTORY = "static"


@app.route("/api/file/read", methods=["POST"])
def read_file():
    """Парсит полученный XML-файл и сохраняет данные в базе данных."""
    file = request.files.get("file")
    if not file:
        return jsonify(False), 400
    filename = file.filename

    file_content = file.read()
    validation_stream = io.BytesIO(file_content)
    parsing_stream = io.BytesIO(file_content)

    if not validate_xml(validation_stream):
        return jsonify({"error": "Incorrect XML"}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Files (name) "
                           "VALUES (?) ON CONFLICT(name) DO NOTHING",
                           (filename,))
            conn.commit()
            cursor.execute("SELECT id FROM Files WHERE name = ?", (filename,))
            file_row = cursor.fetchone()
            if not file_row:
                return jsonify(False), 500
            file_id = file_row[0]

            parser = xml.sax.make_parser()
            handler = XMLHandler(file_id, conn)
            parser.setContentHandler(handler)
            parser.parse(parsing_stream)
        return jsonify(True)
    except xml.sax.SAXException as e:
        return jsonify(False), e
    except Exception as e:
        return jsonify(False)


@app.route("/api/tags/get-count", methods=["GET"])
def get_tag_count():
    file_path = request.args.get("file_path")
    tag_name = request.args.get("tag_name")
    if not file_path or not tag_name:
        return jsonify({"error": "Отсутствует file_path или tag_name"}), 400
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        parser = xml.sax.make_parser()
        handler = TagCounterHandler(tag_name)
        parser.setContentHandler(handler)
        with open(file_path, "r", encoding="utf-8") as file:
            parser.parse(file)
        if handler.count == 0:
            return jsonify(
                {"error": "В файле отсутствует тег с данным названием"}), 404
        return jsonify({"tag_count": handler.count})

    except xml.sax.SAXException:
        return jsonify({"error": "Неверный формат XML"}), 400


@app.route("/api/tags/attributes/get", methods=["GET"])
def get_tag_attributes():
    file_name = request.args.get("file_name")
    tag_name = request.args.get("tag_name")
    if not file_name or not tag_name:
        return jsonify({"error": "Отсутствует file_name или tag_name"}), 400
    file_name = os.path.join(FILE_DIRECTORY, file_name)
    if not os.path.exists(file_name):
        return jsonify({"error": "File not found"}), 404
    try:
        parser = xml.sax.make_parser()
        handler = AttributeCollectorHandler(tag_name)
        parser.setContentHandler(handler)
        with open(file_name, "r", encoding="utf-8") as file:
            parser.parse(file)
        if not handler.tag_found:
            return jsonify(
                {"error": f"В файле нет тега {tag_name}"}), 404
        return jsonify({"attributes": list(handler.attributes)})
    except xml.sax.SAXException:
        return jsonify({"error": "Неверный формат XML"}), 400


if __name__ == "__main__":
    app.run(debug=True)
