class ParserISU:
    def __init__(self, ids_isu: list = None):
        if ids_isu is None:
            ids_isu = []
        self.ids_isu = ids_isu
        self.base_isu_link = 'https://isu.ifmo.ru/person/'
