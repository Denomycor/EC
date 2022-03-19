from probability import ProbDist
from probability import JointProbDist



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
    dimension = list(distIni.prob)[-1] #len(distIni.prob)
    
    fill(var, [], [], dimension, 0, max, distIni, movimentos, donut)

    return var


def fill(var, path, probs, dim, cur, max, distIni, movimentos, donut):
    mov = 0
    cells = range(1, dim+1) if isinstance(dim, int) else createCells(dim)
    if cur != 0:
        mov = go(path[len(path)-1], dim, movimentos, donut)

    for i in cells:
        path.append(i)
        
        if cur == 0:
            probs.append(distIni[i])
        else:       
            probs.append(mov[i] if i in mov else 0)

        if cur == max:
            var[tuple(path)] = mul(probs)
        else:
            fill(var, path, probs, dim, cur+1, max, distIni, movimentos, donut)

        del probs[-1]
        del path[-1]
    


ini=initDist((2,2), {(1,1):0.6, (2,1): 0.4})
f=fantasmaConj(ini, 2, {'E': 0.5, 'S': 0.3, '.': 0.2})

"""
for i in range(1, 4):
    for j in range(1, 4):
        for k in range(1, 4):
            print(f[i,j,k])
"""