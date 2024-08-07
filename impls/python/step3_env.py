import sys, traceback
import mal_readline
import mal_types as types
import reader, printer
from env import Env

# read
def READ(str):
    return reader.read_str(str)

# eval
def EVAL(ast, env):
    dbgeval = env.get_or_nil('DEBUG-EVAL')
    if dbgeval is not None and dbgeval is not False:
        print('EVAL: ' + printer._pr_str(ast))

    if types._symbol_Q(ast):
        return env.get(ast)
    elif types._vector_Q(ast):
        return types._vector(*map(lambda a: EVAL(a, env), ast))
    elif types._hash_map_Q(ast):
        return types.Hash_Map((k, EVAL(v, env)) for k, v in ast.items())
    elif not types._list_Q(ast):
        return ast  # primitive value, return unchanged
    else:

        # apply list
        if len(ast) == 0: return ast
        a0 = ast[0]

        if "def!" == a0:
            a1, a2 = ast[1], ast[2]
            res = EVAL(a2, env)
            return env.set(a1, res)
        elif "let*" == a0:
            a1, a2 = ast[1], ast[2]
            let_env = Env(env)
            for i in range(0, len(a1), 2):
                let_env.set(a1[i], EVAL(a1[i+1], let_env))
            return EVAL(a2, let_env)
        else:
            f = EVAL(a0, env)
            args = ast[1:]
            return f(*(EVAL(a, env) for a in args))

# print
def PRINT(exp):
    return printer._pr_str(exp)

# repl
repl_env = Env()
def REP(str):
    return PRINT(EVAL(READ(str), repl_env))

repl_env.set(types._symbol('+'), lambda a,b: a+b)
repl_env.set(types._symbol('-'), lambda a,b: a-b)
repl_env.set(types._symbol('*'), lambda a,b: a*b)
repl_env.set(types._symbol('/'), lambda a,b: int(a/b))

# repl loop
while True:
    try:
        line = mal_readline.readline("user> ")
        if line == None: break
        if line == "": continue
        print(REP(line))
    except reader.Blank: continue
    except Exception as e:
        print("".join(traceback.format_exception(*sys.exc_info())))
