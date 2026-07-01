import ast
import operator as op

class IAAModule:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ivars = {}
        self.dyvars = {}
        self.dylines = {}
        self.file_lines = []
        self.title = ""
        self.lineno = 0

    def auto(self, value):
        value = value.strip()
        try:
            return int(value)
        except:
            try:
                return float(value)
            except:
                return value


    def safe_eval(self, expr, variables=None):
        variables = variables or {}

        allowed_ops = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.Mod: op.mod,
            ast.UAdd: op.pos,
            ast.USub: op.neg,
        }

        def _eval(node):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Invalid constant")

            if isinstance(node, ast.Name):
                if node.id in variables:
                    return variables[node.id]
                raise ValueError(f"Unknown variable: {node.id}")

            if isinstance(node, ast.BinOp):
                return allowed_ops[type(node.op)](
                    _eval(node.left),
                    _eval(node.right),
                )

            if isinstance(node, ast.UnaryOp):
                return allowed_ops[type(node.op)](
                    _eval(node.operand)
                )

            raise ValueError("Unsafe expression")

        tree = ast.parse(expr, mode="eval")
        return _eval(tree.body)



    def parse_value(self, text):
        text = text.strip()

        # only treat [expr] as expression
        if text.startswith("[") and text.endswith("]"):
            expr = text[1:-1]

            # merge ivars + dyvars for expression context
            vars_context = {**self.ivars, **self.dyvars}

            try:
                return round(self.safe_eval(expr, vars_context), 6)
            except:
                return self.auto(text)

        return self.auto(text)

    def convert_dict_to_vars(self, data):
        for k, v in data.items():
            setattr(self, k, v)



    def parse_iaa(self, file):
        self.reset()

        next_var = 0
        next_dvar = 0
        name = ""

        with open(file, "r") as f:
            self.file_lines = f.readlines()

        for i, raw in enumerate(self.file_lines, start=1):
            line = raw.rstrip("\n")
            stripped = line.strip()

            if stripped.startswith("#"):
                continue

            if stripped.startswith("{") and stripped.endswith("}"):
                self.title = stripped[1:-1]
                continue

            if next_var > 0:
                next_var -= 1
            if next_dvar > 0:
                next_dvar -= 1

            # dynamic var
            if stripped.startswith("dynamic") and stripped.endswith(":"):
                name = stripped.replace("dynamic", "").replace(":", "").strip()
                next_dvar = 2
                continue

            # normal var
            if stripped.endswith(":") and not stripped.startswith("dynamic"):
                name = stripped.replace(":", "").strip()
                next_var = 2
                continue

            # dynamic value line
            if next_dvar == 1 and line.startswith(" "):
                value = self.parse_value(stripped)
                self.dyvars[name] = value
                self.dylines[name] = i

            # normal value line
            elif next_var == 1 and line.startswith(" "):
                value = self.parse_value(stripped)
                self.ivars[name] = value

        self.convert_dict_to_vars(self.ivars)
        self.convert_dict_to_vars(self.dyvars)



    def modify_dynamic(self, var, value, filename):
        if var not in self.dylines:
            return

        index = self.dylines[var] - 1
        lines = self.file_lines[:]

        if 0 <= index < len(lines):
            lines[index] = f" {value}\n"

        with open(filename, "w") as f:
            f.writelines(lines)

        self.parse_iaa(filename)


