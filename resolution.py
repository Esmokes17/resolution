from enum import Enum
from typing import Union

__all__ = ['Operation', 'ClauseSentence', 'parse', 'prove']
__author__ = 'Mahdi Kashani'
__title__ = 'Resolution method'

class Operation(Enum):
    """
        Attributs
        ---------
            NONE : no Operation
            NEGATION : ~
            CONJUNCTION : \\/
            DISJUNCTION : /\\
            IMPLICATION : ->
            EQUIVALENCE : <->

        Methods
        -------
            getOperation(operand)
                return your operand in Operation type
    """
    NONE        = ' '     # a , b
    NEGATION    = '~'     # ~a , ~b
    CONJUNCTION = '\\/'   # a \/ b
    DISJUNCTION = '/\\'   # a /\ b
    IMPLICATION = '->'    # a -> b
    EQUIVALENCE  = '<->'   # a <-> b

    @staticmethod
    def getOperation(operand: str):
        if(operand == '~'):
            return Operation.NEGATION
        elif(operand ==  '\\/'):
            return Operation.CONJUNCTION
        elif(operand == '/\\'):
            return Operation.DISJUNCTION
        elif(operand == '->'):
            return Operation.IMPLICATION
        elif(operand == '<->'):
            return Operation.EQUIVALENCE
        else:
            return Operation.NONE

    @property
    def symbol(self) -> str:
        if(self == Operation.NEGATION):
            return '\u02DC'
        elif(self == Operation.CONJUNCTION):
            return '\u2228'
        elif(self == Operation.DISJUNCTION):
            return '\u2227'
        elif(self == Operation.IMPLICATION):
            return '\u2192'
        elif(self == Operation.EQUIVALENCE):
            return '\u27F7'
        else:
            return ''   

class ClauseSentence:
    clause: Union[tuple, str]
    operand: Operation
    def __init__(self, operand: Operation, clause: tuple):
        if(operand == Operation.NONE):
            assert isinstance(clause, str), "you should use str or tuple with Clause type element"
        else:
            assert all(isinstance(i, ClauseSentence) for i in clause), "you should use str or tuple with Clause type element"
        self.operand = operand
        self.clause = clause

    def toString(self):
        if(self.operand == Operation.NONE):
            return self.clause
        elif(self.operand == Operation.NEGATION):
            return '~'+self.clause[0].clause
    
    def __key(self):
        return(self.operand, self.clause)
    
    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other) -> bool:
        return (isinstance(other, type(self)) and (self.clause, self.operand) == (other.clause, other.operand))        

    def __str__(self):
        if(self.operand == Operation.NONE or self.operand == Operation.NEGATION):
            op = self.operand.symbol
            return f'{op} {str(self.clause.__str__())}'
        op = self.operand.symbol
        return f'{self.clause[0].__str__()} {op} {self.clause[1].__str__()}'

def convert(term: ClauseSentence):
    """ convert implication and equavalnce to disjunction or conjunction"""
    isNegation = False
    if(term.operand == Operation.NEGATION):
        term = term.clause
        isNegation = True
    if(term.operand == Operation.IMPLICATION):
        clause = (applyNegation(ClauseSentence(Operation.NEGATION, (term.clause[0],) )), term.clause[1])
        res = ClauseSentence( Operation.CONJUNCTION, clause )
        if(isNegation):
            return applyNegation(ClauseSentence( Operation.NEGATION, (res,)))
        return res
    elif(term.operand == Operation.EQUIVALENCE):
        clause1 = applyNegation(ClauseSentence( Operation.CONJUNCTION, (applyNegation(ClauseSentence(Operation.NEGATION, (term.clause[0],))), term.clause[1])))
        clause2 = applyNegation(ClauseSentence( Operation.CONJUNCTION, (term.clause[0], applyNegation(ClauseSentence(Operation.NEGATION, (term.clause[1],))))))
        res = ClauseSentence(Operation.DISJUNCTION, (clause1, clause2))
        if(isNegation):
            return applyNegation(ClauseSentence( Operation.NEGATION, (res,)))
        return res

def simplificationNegation(term: ClauseSentence):
    while(term.operand == Operation.NEGATION and term.clause[0].operand == Operation.NEGATION):
        term = term.clause[0].clause[0]
    return term

def distribution(term: ClauseSentence):
    if(term.operand in [Operation.NEGATION, Operation.NONE]):
        return None
    elif(
        not term.clause[0].operand == Operation.NONE
        and term.clause[1].operand == Operation.NONE
        and not term.clause[0].operand == term.operand
        and term.clause[0].operand == Operation.DISJUNCTION
        and term.operand == Operation.CONJUNCTION
    ):
        clause1 = ClauseSentence(term.operand, (term.clause[0].clause[0], term.clause[1]))
        clause2 = ClauseSentence(term.operand, (term.clause[0].clause[1], term.clause[1]))
        return ClauseSentence(term.clause[0].operand, (clause1, clause2))

    elif(
        not term.clause[1].operand == Operation.NONE
        and term.clause[0].operand == Operation.NONE
        and not term.clause[1].operand == term.operand
        and term.clause[1].operand == Operation.DISJUNCTION
        and term.operand == Operation.CONJUNCTION
    ):
        clause1 = ClauseSentence(term.operand, (term.clause[1].clause[0], term.clause[0]))
        clause2 = ClauseSentence(term.operand, (term.clause[1].clause[1], term.clause[0]))
        return ClauseSentence(term.clause[1].operand, (clause1, clause2))

def splitByDisjunction(term: ClauseSentence):
    result = []
    if(term.operand == Operation.NEGATION):
        term = applyNegation(term)
    if(term.operand == Operation.DISJUNCTION):
        clause1 = term.clause[0]
        clause2 = term.clause[1]
        if(not clause1.operand == Operation.NONE and not (clause1.operand == Operation.NONE and clause1.clause[0].operand == Operation.NEGATION)):
            result += (splitByDisjunction(clause1))
        else:
            result.append({clause1.toString()})
        if(not clause2.operand == Operation.NONE and not (clause2.operand == Operation.NONE and clause1.clause[0].operand == Operation.NEGATION)):
            result += (splitByDisjunction(clause2))
        else:
            result.append({clause2.toString()})
        return result
    elif(term.operand == Operation.CONJUNCTION):
        clause1 = splitByDisjunction(term.clause[0])
        clause2 = splitByDisjunction(term.clause[1])
        return clause1 + clause2
    else:
        return [set([term.toString()])]

def subscription(premise1: set, premise2: set):
    for pre1 in premise1:
        for pre2 in premise2:
            if(pre1[-1] == pre2[-1]):
                temp = premise1.copy()
                temp.remove(pre1)
                temp |= premise2.copy()
                temp = temp
                temp.remove(pre2)
                yield (temp)

def applyNegation(term: ClauseSentence):
    if(not term.operand == Operation.NEGATION):
        return term
    else:
        term = term.clause[0]
        if(term.operand in [Operation.EQUIVALENCE, Operation.IMPLICATION]):
            term = convert(term)
        if(term.operand == Operation.CONJUNCTION):
            clause1 = applyNegation(simplificationNegation(ClauseSentence(Operation.NEGATION, (term.clause[0],))))
            clause2 = applyNegation(simplificationNegation(ClauseSentence(Operation.NEGATION, (term.clause[1],))))
            return ClauseSentence( Operation.DISJUNCTION, (clause1 , clause2) )
        elif(term.operand == Operation.DISJUNCTION):
            clause1 = applyNegation(simplificationNegation(ClauseSentence(Operation.NEGATION, (term.clause[0],))))
            clause2 = applyNegation(simplificationNegation(ClauseSentence(Operation.NEGATION, (term.clause[1],))))
            return ClauseSentence( Operation.CONJUNCTION, (clause1 , clause2) )
        elif(term.operand == Operation.NEGATION):
            return applyNegation(term.clause[0])
        else:
            return ClauseSentence(Operation.NEGATION, (term,))

def isProvable(premises: list):
    """
        if clauses can prove conlusion return True otherwise False
    """
    for pre in premises:
        for other in premises:
            if(other != pre):
                new = subscription(pre, other)
                for x in new:
                    if(x == None):
                        continue
                    elif(len(x) == 0):
                        return True
                    elif(not x in premises):
                        premises.append(x)
    return False

def prove(premises: list[str], conclusion: list[str]):
    tempPremises = premises.copy()
    if (conclusion != ""):
    tempPremises.append('~ ( ' + conclusion + ' )')
    premisesClause = []
    for pre in tempPremises:
        is_Negation = False
        clause = parse(pre.split())
        if(not clause.operand == Operation.NONE):
            if(clause.operand == Operation.NEGATION):
                clause = simplificationNegation(clause)
            if(clause.operand == Operation.IMPLICATION or clause.operand == Operation.EQUIVALENCE):
                clause = convert(clause)
            res = distribution(clause)
            if(not res == None):
                clause = res
        premisesClause += splitByDisjunction(clause)
    
    temp = []
    [temp.append(x) for x in premisesClause if x not in temp]
    premisesClause = temp
    return isProvable(premisesClause), premisesClause

def parse(input: list) -> ClauseSentence:
    """
        parse a logic term to a ClauseSentence

        Parameter
        ---------
        input: list 
            operation and clauses of a term

        Return
        ------
        ClauseSentence
            operation and clause inform a ClauseSentence object 
        Examples
        -------
            >>> rawInput = 'p -> q'
            >>> input = rawInput.split()
            >>> print(parse(input))
            (<Operation.IMPLICATION: '->'>, ((<Operation.NONE: ' '>, 'p'), (<Operation.NONE: ' '>, 'q')))
            >>> rawInput = '( ~ p) \\/ ( q <->)'
            >>> input = rawInput.split()
            >>> print(parse(input))
            (<Operation.DISJUNCTION: '/\'>, ((<Operation.NEGATION: '~'>, ((<Operation.NONE: ' '>, 'p'),)), (<Operation.EQUVALENCE: '<->'>, ((<Operation.NONE: ' '>, 'q'), (<Operation.NONE: ' '>, 'p')))))
    """
    if(len(input) == 1):
        return ClauseSentence( Operation.NONE, input[0] )
    i = 0
    while (i != len(input)):
        if(input[i] == '('):
            begin = i+1
            countBraces = 0
            i+=1
            while(True):
                if(input[i] == '('):
                    countBraces += 1
                elif(input[i] == ')'):
                    if(countBraces == 0):
                        break
                    else:
                        countBraces -= 1
                i+=1
            if (begin == 1 and i == len(input)-1):
                return parse(input[begin:i])

        if(Operation.getOperation(input[0]) == Operation.NEGATION):
            clause = parse(input[i+1:])
            return ClauseSentence( Operation.getOperation(input[i]), (clause,) )
        if(Operation.getOperation(input[i]) != Operation.NONE):
            clause = ( parse(input[0:i]), parse(input[i+1:len(input)]) )
            return ClauseSentence( Operation.getOperation(input[i]) , clause )
        i+=1

if __name__ == "__main__":
    import cmd
    commands = []
    class CmdParse(cmd.Cmd):
        intro = 'Welcome to the resolution shell.   Type help or ? to list commands.\n' 
        prompt = "> "
        def default(self, line):
            line = line.split(',')
            if len(line) == 1:
                print(prove(line))
            else:
                print(prove(line[:-1], line[-1]))
            commands.append(line)
        def do_help(self, line):
            if line == "exit":
                print(self.do_exit.__doc__)
            else:
                print(" your clause should be written with space between symbols and variable and also put tuple variable in ( )")
        def empty(self, line):
            self.do_help()
        def do_exit(self, arg):
            """ exit from shell mode """
            exit(0)
    CmdParse().cmdloop()