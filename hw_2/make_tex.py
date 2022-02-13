from hw_1 import main as build_ast_tree
import subprocess


def start_document():
    return '\\documentclass[a4paper, 12pt]{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage[english]{babel}\n\\usepackage{graphicx}\n\n\\begin{document}\n\n'


def end_document():
    return '\n\\end{document}'


def generate_tex_document(text):
    return start_document() + text + end_document()


def start_table():
    return '\\begin{table}[]\n'


def end_table():
    return '\\end{table}\n'


def start_tabular(len):
    return '\\begin{tabular}{' + 'l' * len + '}\n'


def end_tabular():
    return '\\end{tabular}\n'


def process_table(table):
    tex = ' \\\\\n'.join(map(lambda line: ' & '.join(map(lambda x: str(x), line)), table)) + '\n'
    return tex


def generate_tex_table(table):
    return start_table() + start_tabular(len(table[0])) + process_table(table) + end_tabular() + end_table()


def generate_image_tex(image_path):
    return '\\includegraphics[width=\\textwidth]{' + image_path + '}\n'


def main():
    table = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    image = 'artifacts/graph.png'
    build_ast_tree()

    table_tex = generate_tex_table(table)
    image_tex = generate_image_tex(image)
    document = generate_tex_document(table_tex + '\n' + image_tex)
    with open('artifacts/document.tex', 'w') as f:
        print(document, file=f)

    proc = subprocess.Popen(['pdflatex', '-output-directory=artifacts', 'artifacts/document.tex'])
    proc.communicate()


if __name__ == '__main__':
    main()
