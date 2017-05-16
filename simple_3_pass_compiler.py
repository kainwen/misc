"""
Tiny Three-Pass Compiler
https://www.codewars.com/kata/5265b0885fda8eac5900093b/
"""


import re
import itertools


class Compiler(object):

    def compile(self, program):
        return self.pass3(self.pass2(self.pass1(program)))

    def tokenize(self, program):
        """Turn a program string into an array of tokens.  Each token
           is either '[', ']', '(', ')', '+', '-', '*', '/', a variable
           name or a number (as a string)"""
        token_iter = (m.group(0) for m in re.finditer(r'[-+*/()[\]]|[A-Za-z]+|\d+', program))
        return [int(tok) if tok.isdigit() else tok for tok in token_iter]

    def parse_var(self, toks):
        if re.match('[a-zA-Z]+', toks[0]):
            return ('var', toks[0]), toks[1:]
        else:
            raise

    def parse_factor(self, toks):
        if type(toks[0]) == type(0):
            num, r = self.parse_num(toks)
            return ('factor', num), r
        elif re.match("[a-zA-Z]", toks[0]):
            var, r = self.parse_var(toks)
            return ('factor', var), r
        elif toks[0] == '(':
            exp, r = self.parse_exp(toks[1:])
            return ('factor', exp), r[1:]
        else:
            raise

    def parse_num(self, toks):
        if type(toks[0]) == type(0):
            return ('num', toks[0]), toks[1:]
        else:
            raise

    def parse_term(self, toks):
        term, r = self.parse_multi_with_delim(self.parse_factor,
                                              toks,
                                              re_delim=r"[*]|[/]",
                                              in_result=True)
        return ('term', self.left_combine(term, "term")), r


    def parse_exp(self, toks):
        exp, r = self.parse_multi_with_delim(self.parse_term,
                                             toks,
                                             re_delim=r"[+]|-",
                                             in_result=True)
        return ('exp', self.left_combine(exp, "exp")), r

    def left_combine(self, lst, name):
        if len(lst) == 1:
            return lst[0]
        elif len(lst) == 3:
            first, op, final = lst
            return (op, first, final)
        else:
            left = self.left_combine(lst[:-2], name)
            op = lst[-2]
            final = lst[-1]
            return (op, (name, left), final)

    def parse_function(self, toks):
        var_list, r = self.parse_multi_with_delim(self.parse_var, toks[1:])
        env = dict(zip([v for _, v in var_list],
                       range(0, len(var_list))))
        exp, r1 = self.parse_exp(r[1:])
        assert r1 == []
        return ('function', env, exp)

    def parse_multi_with_delim(self, pf, toks, re_delim=None, in_result=False):
        if not toks:
            return [], []
        result = []
        curr = toks
        while True:
            try:
                e, r = pf(curr)
            except:
                return result, curr
            result.append(e)
            curr = r
            if not curr:
                return (result, [])
            if re_delim is None:
                curr = r
            else:
                if re.match(re_delim, r[0]):
                    if in_result:
                        result.append(r[0])
                        curr = r[1:]
                    else:
                        curr = r[1:]
                else:
                    return result, curr

    def gen_json_ast(self, ast):
        if ast[0] == 'exp':
            return self.gen_json_ast_exp(ast)
        if ast[0] == 'term':
            return self.gen_json_ast_term(ast)
        if ast[0] == 'factor':
            return self.gen_json_ast_factor(ast)

    def gen_json_ast_exp(self, nast):
        name, ast = nast
        if type(ast) == type(()) and ast[0] == 'term':
            return self.gen_json_ast_term(ast)
        if type(ast) == type(()) and ast[0] in ["+", "-"]:
            return {
                "op": ast[0],
                "a": self.gen_json_ast(ast[1]),
                "b": self.gen_json_ast(ast[2])
            }

    def gen_json_ast_term(self, nast):
        name, ast = nast
        if type(ast) == type(()) and ast[0] == 'factor':
            return self.gen_json_ast_factor(ast)
        if type(ast) == type(()) and ast[0] in ["*", "/"]:
            return {
                "op": ast[0],
                "a": self.gen_json_ast(ast[1]),
                "b": self.gen_json_ast(ast[2])
            }

    def gen_json_ast_factor(self, nast):
        name, ast = nast
        if type(ast) == type(()) and ast[0] == 'num':
            return {"op": "imm", "n": ast[1]}
        if type(ast) == type(()) and ast[0] == 'var':
            return {"op": "arg", "n": self.env[ast[1]]}
        return self.gen_json_ast(ast)

    def pass1(self, program):
        """Returns an un-optimized AST"""
        tokens = self.tokenize(program)
        func = self.parse_function(tokens)
        (name, env, exp) = func
        self.env = env
        jexp = self.gen_json_ast(exp)
        return jexp

    def is_imm(self, ast):
        return ast["op"] == "imm"

    def calc_imm(self, ast1, ast2, op):
        return {
            "op": "imm",
            "n": self.op_calc(op, ast1["n"], ast2["n"])
        }

    def op_calc(self, op, n1, n2):
        if op == "+": return n1 + n2
        if op == "*": return n1 * n2
        if op == "-": return n1 - n2
        if op == "/": return n1 / n2

    def is_zero(self, ast):
        return ast["op"] == "imm" and ast["n"] == 0

    def is_one(self, ast):
        return ast["op"] == "imm" and ast["n"] == 1

    def reduce(self, ast):
        if ast["op"] in ["+", "-", "*", "/"]:
            a = self.reduce(ast["a"])
            b = self.reduce(ast["b"])
            if self.is_imm(a) and self.is_imm(b):
                return self.calc_imm(a, b, ast["op"])
            if ast["op"] == "+":
                if self.is_zero(a): return b
                if self.is_zero(b): return a
            if ast["op"] == "-":
                if self.is_zero(b): return a
            if ast["op"] == "*":
                if self.is_zero(a) or self.is_zero(b): return {"op": "imm", "n": 0}
                if self.is_one(a): return b
                if self.is_one(b): return a
            if ast["op"] == "/":
                if self.is_zero(a): return {"op": "imm", "n": 0}
                if self.is_one(b): return a
            return {"op": ast["op"], "a": a, "b": b}
        return ast

    def pass2(self, ast):
        return self.reduce(ast)

    def pass3(self, ast):
        return self.code_gen(ast)

    def get_inst(self, op):
        INST = {
            "+": "AD",
            "-": "SU",
            "*": "MU",
            "/": "DI",
        }
        return [INST[op]]

    def save_r1(self):
        return [
            "SW",
            "PU",
            "SW"
        ]

    def restore_r1(self):
        return [
            "SW",
            "PO",
            "SW"
        ]

    def code_gen(self, ast):
        if ast["op"] in ["+", "-", "*", "/"]:
            a, b = ast["a"], ast["b"]
            insts_a = self.code_gen(a)
            swi_inst1 = ["SW"]
            insts_b = self.code_gen(b)
            swi_inst2 = ["SW"]
            insts = itertools.chain(self.save_r1(),
                                    insts_a,
                                    swi_inst1,
                                    insts_b,
                                    swi_inst2,
                                    self.get_inst(ast["op"]),
                                    self.restore_r1())
            return list(insts)

        if ast["op"] == "imm":
            return ["IM {n}".format(n=ast["n"])]
        if ast["op"] == "arg":
            return ["AR {n}".format(n=ast["n"])]
