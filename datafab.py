from random import randint, choice
from datetime import datetime, date
from collections.abc import Generator
import re
from string import ascii_lowercase, ascii_uppercase


class Person:
    men: list = ['Santiago', 'Mateo', 'Sebastian', 'Leonardo', 'Matias', 'Emiliano', 'Diego', 'Miguel Angel',
                 'Daniel', 'Alexander', 'Alejandro', 'Jesus', 'Gael']

    women: list = ['Sofia', 'Maria Jose', 'Valentina', 'Ximena', 'Regina', 'Camila', 'Maria Fernanda', 'Valeria',
                   'Renata', 'Victoria', 'Natalia', 'Daniela', 'Isabella']

    name_list: list = [men, women]

    genre_settings: list = [["H", 0], ["M", 1]]

    name: str

    genre: str

    def name_selection(self):
        selected = choice(self.genre_settings)
        self.genre = selected[0]
        self.name = choice(self.name_list[selected[1]])
        return None

    def __init__(self):
        self.name_selection()

    def __str__(self):
        return self.name


class LastName:
    last_name_list: list = ['Hernandez', 'Garcia', 'Martinez', 'Lopez', 'Gonzalez', 'Perez', 'Rodriguez', 'Sanchez',
                            'Ramirez', 'Cruz', 'Flores', 'Gomez', 'Morales', 'Vazquez', 'Reyes', 'Jimenez', 'Torres',
                            'Diaz', 'Gutierrez', 'Ruiz', 'Mendoza', 'Aguilar', 'Aguirre', 'Sola', 'Guzman', 'Peralta',
                            'Ortiz', 'Moreno', 'Castillo', 'Romero']

    def __str__(self):
        return choice(self.last_name_list)


def range_code(start: int, end: int):
    while True:
        code = randint(start, end)
        yield code


def consec(start_with: int = 1, incremented_by: int = 1):
    while True:
        yield start_with
        start_with += incremented_by


def random_date(form: str = '%d-%m-%Y'):
    minyear = 1980
    maxyear = date.today().year+2
    while True:
        try:
            selected_date = datetime(randint(minyear, maxyear), randint(1, 12), randint(1, 31))
        except ValueError:
            continue

        yield selected_date.strftime(form)


def regex_code(pattern: str):
    orders = []
    general_index = [obj.span() for obj in re.finditer(r'\\\w\{\d+}', pattern)]
    index_digits = [number.span() for number in re.finditer(r'\\d\{\d+}', pattern)]
    index_lower = [letter.span() for letter in re.finditer(r'\\l\{\d+}', pattern)]
    general_repeats = [int(num.group()) for obj in re.finditer(r'\\\w\{\d+}', pattern) for num in re.finditer(r'\d+', obj.group())]
    for index in general_index:
        if index in index_digits:
            repeat = int(re.findall('\d+', pattern[index[0]:index[1]])[0])
            orders.extend(['digit' for n in range(repeat)])
        elif index in index_lower:
            repeat = int(re.findall('\d+', pattern[index[0]:index[1]])[0])
            orders.extend(['lower' for n in range(repeat)])
        else:
            repeat = int(re.findall('\d+', pattern[index[0]:index[1]])[0])
            orders.extend(['upper' for n in range(repeat)])

    #Sorting
    general_index.sort(reverse=True)
    general_repeats = [number for _, number in sorted(enumerate(general_repeats), key=lambda number: number[1], reverse=True)]

    for index_repeats, index in enumerate(general_index):
        repeat = int(general_repeats[index_repeats])
        replace = 'ñ0Q'*repeat
        pattern = pattern[:index[0]]+replace+pattern[index[1]:]

    while True:
        product = pattern
        for order in orders:
            if order == 'digit':
                product = product.replace('ñ0Q', str(randint(0, 9)), 1)
            elif order == 'lower':
                product = product.replace('ñ0Q', choice(ascii_lowercase), 1)
            else:
                product = product.replace('ñ0Q', choice(ascii_uppercase), 1)

        yield product


class Datafab:

    modules: dict = {1: Person, 2: [Person, 'genre'], 3: LastName, 4: date.today(), 5: consec()}
    lay_out: list

    def __init__(self, query):
        query = [pop_list.split("=") for pop_list in query.split("\n")]
        num_error = 0
        for indice in range(0, len(query)):
            try:
                num_module = query[indice - num_error][1]
                query[indice - num_error][1] = int(num_module)
            except IndexError:
                query.pop(indice - num_error)
                num_error += 1

        self.lay_out = query

    def generate_rows(self, row_amount: int, header: bool = True):
        rows = [[] for repeat in range(row_amount)]
        classused = dict()

        for order_index, num in enumerate(self.lay_out):
            quobj = self.modules[num[1]]
            if type(quobj) is list:
                if quobj[0] in classused:
                    for index in range(row_amount):
                        obj = rows[index][classused[quobj[0]]]
                        attr = getattr(obj, quobj[1])
                        rows[index].append(attr)
                else:
                    for index in range(row_amount):
                        obj = quobj[0]()
                        attr = getattr(obj, quobj[1])
                        rows[index].append(attr)

                    classused[quobj[0]] = order_index

            elif type(quobj) is type:
                if quobj in classused:
                    for index in range(row_amount):
                        rows[index].append(rows[index][classused[quobj]])
                else:
                    for index in range(row_amount):
                        obj = quobj()
                        rows[index].append(obj)

                    classused[quobj] = order_index

            elif isinstance(quobj, Generator):
                for index in range(row_amount):
                    rows[index].append(next(quobj))

            else:
                for index in range(row_amount):
                    rows[index].append(quobj)

        if header:
            header_cols = [column[0] for column in self.lay_out]
            rows.insert(0, header_cols)

        return rows

    def generate_file(self, row_amount: int, path: str, delimiter: str = ',', header: bool = True):
        rows = self.generate_rows(row_amount, header=header)
        with open(path, 'w') as file:
            for row in rows:
                row = [str(element) for element in row]
                file.write(f'{delimiter.join(row)}\n')

    def __str__(self):
        result = ''
        for key, value in self.modules.items():
            result += f'{key}: {value}\n'

        return result[:-1]
