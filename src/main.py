from probability import ProbDist, enumerate_joint, enumerate_joint_ask
from probability import JointProbDist
from prettytable import PrettyTable


def printSorted(dicionario):
    print({k:v for (k,v) in sorted(dicionario.items())})

def clamp(lhs, c, rhs):
    return max(lhs, min(c, rhs))

def rotate(lhs, c, rhs):
    if c == rhs+1:
        return lhs
    if c == lhs-1:
        return rhs
    return c

def addTuple(t1, t2):
    return (t1[0]+t2[0], t1[1]+t2[1])

def mul(ls):
    acc = 1
    for e in ls:
        acc *= e
    return acc

def createCells(dimensao):
    res = []
    for i in range(1, dimensao[0]+1):
        for j in range(1, dimensao[1]+1):
            res.append((i,j))
    return res

def enumerate_joint_prob(evidencia, conjunta):
    variaveis = [v for v in conjunta.variables if not v in evidencia] 
    return enumerate_joint(variaveis,evidencia,conjunta)

#################################################

def initDist(dimensao, celulas):
    var = ProbDist("X0")
    if isinstance(dimensao, int) and isinstance(celulas, list):
        for i in range(1,dimensao+1):
            var[i] = 1/len(celulas) if i in celulas else 0

    elif isinstance(dimensao, int) and isinstance(celulas, dict):
        for i in range(1,dimensao+1):
            var[i] = celulas[i] if i in celulas else 0

    elif isinstance(dimensao, tuple) and isinstance(celulas, list):
        for i in range(1, dimensao[0]+1):
           for j in range(1, dimensao[1]+1): 
               var[(i,j)] = 1/len(celulas) if (i,j) in celulas else 0

    elif isinstance(dimensao, tuple) and isinstance(celulas, dict):
        for i in range(1, dimensao[0]+1):
           for j in range(1, dimensao[1]+1): 
               var[(i,j)] = celulas[(i,j)] if (i,j) in celulas else 0

    else:
        print("Error - input in wrong format")

    return var


def go(celula, dimensao, movimentos, donut = False):
    d1 = {'E': 1, 'O': -1, '.': 0}
    d2 = {'E': (0,1), 'O': (0,-1), '.': (0,0), 'S': (1,0), 'N': (-1,0)}
    res = {}
    if isinstance(dimensao, int):
        for m in movimentos:
            dif = d1[m]
            pos = rotate(1, celula+dif, dimensao) if donut else clamp(1, celula+dif, dimensao)
            if pos not in res:
                res[pos] = 0
            res[pos] += 1/len(movimentos) if isinstance(movimentos, list) else movimentos[m]
    
    elif isinstance(dimensao, tuple):
        for m in movimentos:
            sum = addTuple(celula, d2[m])
            pos = (rotate(1, sum[0], dimensao[0]), rotate(1, sum[1], dimensao[1])) if donut else (clamp(1, sum[0], dimensao[0]), clamp(1, sum[1], dimensao[1]))
            if pos not in res:
                res[pos] = 0
            res[pos] += 1/len(movimentos) if isinstance(movimentos, list) else movimentos[m]

    return res


def fantasmaConj(distIni, max, movimentos, donut=False):
    name = []
    for i in range(0, max+1):
        name.append("X"+str(i))
        
    var = JointProbDist(name)
    dim = list(distIni.prob)[-1] #len(distIni.prob)
    cells = range(1, dim+1) if isinstance(dim, int) else createCells(dim)
    
    fill(var, [], [], cells, 0, max, distIni, movimentos, donut)

    return var


def fill(var, path, probs, cells, cur, max, distIni, movimentos, donut):
    mov = 0
    if cur != 0:
        mov = go(path[len(path)-1], cells[-1], movimentos, donut)

    for i in cells:
        path.append(i)
        
        if cur == 0:
            probs.append(distIni[i])
        else:       
            probs.append(mov[i] if i in mov else 0)

        if cur == max:
            var[tuple(path)] = mul(probs)
        else:
            fill(var, path, probs, cells, cur+1, max, distIni, movimentos, donut)

        del probs[-1]
        del path[-1]
    

def probCondFantasma(pergunta, evidencia, conjunta):
    dic = {**pergunta, **evidencia} if evidencia else pergunta
    res = enumerate_joint_prob(dic, conjunta)
    ev = enumerate_joint_prob(evidencia, conjunta) if evidencia else 1
    return res/ev if ev != 0 else 0


def maxProb(conjunta, i):
    inst = "X"+str(i)
    probs = [enumerate_joint_prob({inst : cel}, conjunta) for cel in conjunta.values(inst)]
    val = max(probs)
    res = []
    for i in range(len(conjunta.values(inst))):
        if probs[i] == val:
            res.append(conjunta.values(inst)[i])
    return (res, val)
###########################################################################

def display(f):
    pretty=PrettyTable()
    aux = f.variables.copy()
    aux.append('Prob')
    pretty.field_names = aux 
    #print(pretty.field_names)
    for i in list(f.prob.keys()):
        #print(i)
        pretty.add_row(i+(f[i],))
    print(pretty)


ini=initDist(3,{1:0.6, 3: 0.4})
f=fantasmaConj(ini, 2,{'E':0.3, 'O':0.2,'.':0.5})

ini_1D = initDist(5, {1:0.6,3:0.4})
f_1D = fantasmaConj(ini_1D, 6, {'E':0.3, 'O':0.2,'.':0.5})

ini_2D=initDist((3,3),[(1,1)])
f_2D=fantasmaConj(ini_2D,3,['E','.', 'O', 'S'])

#fantasmaConj 1D test
display(f)
#probCondFantasma 1D test
print(probCondFantasma(dict(X1=3), {}, f_1D))
print(probCondFantasma(dict(X1=2,X2=3), {}, f_1D))
print(probCondFantasma(dict(X0=3,X1=3,X2=3,X3=3), {}, f_1D))
print(probCondFantasma(dict(X3=3), dict(X1=3), f_1D))
print(probCondFantasma(dict(X3=3), dict(X1=2), f_1D))
print(probCondFantasma(dict(X1=2,X2=3), dict(X3=2, X4 = 4), f_1D))
#probCondFantasma 2D test
print(probCondFantasma({'X1':(1,2)}, dict(X3=(2,3)), f_2D))
print(probCondFantasma({'X1':(2,1)}, dict(X3=(2,3)), f_2D))
#maxProb 1D test
print(maxProb(f_1D, 3))
