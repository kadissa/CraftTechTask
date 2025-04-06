import xml.sax


class XMLFileValidator(xml.sax.ContentHandler):
    """Валидатор XML-файла"""

    def __init__(self):
        super().__init__()
        self.valid = True

    def startElement(self, name, attrs):
        pass

    def endElement(self, name):
        pass


class XMLHandler(xml.sax.ContentHandler):
    """
    Обработчик SAX для парсинга XML.
    При обнаружении тега сохраняет его в таблицу Tags, а атрибуты – в таблицу Attributes.
    """

    def __init__(self, file_id, conn):
        super().__init__()
        self.file_id = file_id
        self.conn = conn
        self.cursor = conn.cursor()

    def startElement(self, tag, attrs):
        self.cursor.execute("INSERT INTO Tags (name, file_id) VALUES (?, ?)",
                            (tag, self.file_id))
        tag_id = self.cursor.lastrowid

        for attr_name, attr_value in attrs.items():
            self.cursor.execute(
                "INSERT INTO Attributes (name, value, tag_id) VALUES (?, ?, ?)",
                (attr_name, attr_value, tag_id))

    def endDocument(self):
        self.conn.commit()


class TagCounterHandler(xml.sax.ContentHandler):
    """Обработчик для подсчёта количества указанных тегов"""

    def __init__(self, target_tag):
        super().__init__()
        self.target_tag = target_tag
        self.count = 0

    def startElement(self, tag, attrs):
        if tag == self.target_tag:
            self.count += 1


class AttributeCollectorHandler(xml.sax.ContentHandler):
    """Обработчик SAX для сбора уникальных атрибутов указанного тега"""

    def __init__(self, target_tag):
        super().__init__()
        self.target_tag = target_tag
        self.attributes = set()
        self.tag_found = False

    def startElement(self, tag, attrs):
        if tag == self.target_tag:
            self.tag_found = True
            for attr_name in attrs.keys():
                self.attributes.add(attr_name)


def validate_xml(file):
    """Валидация пришедшего XML."""
    try:
        parser = xml.sax.make_parser()
        validator = XMLFileValidator()
        parser.setContentHandler(validator)
        parser.parse(file)
        return validator.valid
    except xml.sax.SAXException:
        print(f"XML Validation Error: {str(e)}")  # Логирование ошибки
        return False
