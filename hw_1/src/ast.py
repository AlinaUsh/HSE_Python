import inspect
import ast
import astunparse
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout


def fibonacci(n):
    if n <= 0:
        return []
    if n == 1:
        return [0]
    if n == 2:
        return [0, 1]
    result = [0, 1]
    for i in range(n - 2):
        result.append(result[-1] + result[-2])
    return result


class viz_walker(ast.NodeVisitor):
    def __init__(self):
        self.stack = []
        self.graph = nx.Graph()
        self.labeldict = {}
        self.colors = []

    def set_color(self, name):
        if name in ['Module', 'Interactive', 'Expression', 'FunctionType']:
            return 'lightgreen'
        if name in [
                    'FunctionDef', 'AsyncFunctionDef', 'ClassDef', 'Return', 'Delete', 
                    'Assign', 'AugAssign', 'AnnAssign', 'For', 'AsyncFor', 'While', 'If', 
                    'With', 'AsyncWith', 'Match', 'Raise', 'Try', 'Assert', 'Import', 
                    'ImportFrom', 'Global', 'Nonlocal', 'Expr', 'Pass', 'Break', 'Continue'
                   ]:
            return 'lightblue'
        if name in [
                    'BoolOp', 'NamedExpr', 'BinOp', 'UnaryOp', 'Lambda', 'IfExp', 'Dict', 
                    'Se', 'ListComp', 'SetComp', 'DictComp', 'GeneratorExp', 'Await', 
                    'Yield', 'YieldFrom', 'Compare', 'Call', 'FormattedValue', 
                    'JoinedStr', 'Constant', 'Attribute', 'Subscript', 'Starred', 
                    'Name', 'List', 'Tuple', 'Slice'
                   ]:
            return 'lightpink'
        if name in ['Load', 'Store', 'Del']:
            return 'lightgrey'
        if name in ['And', 'Or']:
            return 'lightsteelblue'
        if name in ['Add', 'Sub', 'Mult', 'MatMult', 'Div', 'Mod', 'Pow', 'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd', 'FloorDiv']:
            return 'lightyellow'
        if name in ['Invert', 'Not', 'UAdd', 'USub']:
            return 'lightsalmon'
        if name in ['Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn']:
            return 'aquamarine'
        if name == 'arg':
            return 'lime'
        if name == 'Num':
            return 'orange'
        return 'red'

    def set_text(self, node_type, full_info):
        full_info = astunparse.unparse(full_info).split()
        if node_type in ['Name', 'arg']:
            return '"' + str(full_info[0]) + '"'
        if node_type == 'Num':
            return str(full_info[0])
        if node_type == 'Compare':
            return str(full_info[1])
        if node_type == 'UnaryOp':
            return str(full_info[0][1])
        if node_type == 'BinOp':
            return str(full_info[len(full_info) // 2])
        return ''

    def generic_visit(self, stmt):
        node_name = str(stmt) + str(len(self.colors))
        node_type = type(stmt).__name__
        
        if node_type in ['Load', 'Store', 'Del'] + \
            ['Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn'] + \
            ['Invert', 'Not', 'UAdd', 'USub'] + \
            ['Add', 'Sub', 'Mult', 'MatMult', 'Div', 'Mod', 'Pow', 'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd', 'FloorDiv']:
            return

        
        parent_name = None
        self.labeldict[node_name] = node_type + '\n' + self.set_text(node_type, stmt)
        self.colors.append(self.set_color(node_type))

        if self.stack:
            parent_name = self.stack[-1]

        self.stack.append(node_name)

        self.graph.add_node(node_name)

        if parent_name:
            self.graph.add_edge(node_name, parent_name)

        super(self.__class__, self).generic_visit(stmt)

        self.stack.pop()


def main():
    tree = ast.parse(inspect.getsource(fibonacci))
    mw = viz_walker()
    mw.visit(tree)

    G = mw.graph
    pos = graphviz_layout(G, prog='dot')

    plt.figure(3, figsize=(20, 20), dpi=100)
    nx.draw(
        G, 
        pos,
        labels=mw.labeldict, 
        node_color=mw.colors,
        with_labels = True,
        node_shape='s',
        font_size=10,
        node_size=3500
    )
    plt.show()
    plt.savefig('graph.png')


if __name__ == "__main__":
    main()
