from anytree import Node
from anytree import RenderTree
import anytree
from scanner import scanner
import CodeGenerator
from CodeGenerator import generate_code
from CodeGenerator import program_block
import SemanticChecker
#from Code_gen import Code_gen
#from codegen import *
#import codegen

grammar = {
    
    'Program': [['DeclarationList','$']],
    'DeclarationList' : [['Declaration', 'DeclarationList'],['EPSILON']], 
    'Declaration' : [['DeclarationInitial',  'DeclarationPrime']],
    'DeclarationInitial' : [['TypeSpecifier', '#push_type' , 'ID', '#push']],
    'DeclarationPrime' : [['#start_function' ,'FunDeclarationPrime'], ['VarDeclarationPrime']],
    'VarDeclarationPrime' : [['#variable_definition',';'],['[', 'NUM' , '#push' , '#define_array', ']', ';']], 
    'FunDeclarationPrime' : [ ['(', 'Params', ')', '#define_function', 'CompoundStmt', '#END_SCOPE', '#end_function']],
    'TypeSpecifier': [['int'], ['void']],
    'Params': [['int', '#push', 'ID', '#push', 'ParamPrime', '#add_param', 'ParamList'], ['void']],
    'ParamList': [[',', 'Param', 'ParamList'], ['EPSILON']],
    'Param': [ ['DeclarationInitial', 'ParamPrime', '#add_param']],
    'ParamPrime': [['[', ']', '#push_array_input_type'],['EPSILON', '#push_normal_input_type']] ,
    'CompoundStmt': [['{' ,'DeclarationList', 'StatementList', '}']],
    'StatementList' :[[ 'Statement', 'StatementList'],['EPSILON']],  
    'Statement' : [['ExpressionStmt'], ['CompoundStmt'], ['SelectionStmt'], ['IterationStmt' ],['ReturnStmt']],
    'ExpressionStmt' : [['Expression', '#pop',';'], ['break', '#break',';'], [';']],
    'SelectionStmt' : [['if', '(', 'Expression', '#if', ')', 'Statement', 'else', '#else', 'Statement', '#endif']],
    'IterationStmt' :[[ 'while', '(', '#start_while', 'Expression', ')', '#while_condition', 'Statement', '#endwhile']], 
    'ReturnStmt' :[['return', 'ReturnStmtPrime']],
    'ReturnStmtPrime':[['#return' ,';'],['Expression', '#return_value', ';']],
    'Expression': [['SimpleExpressionZegond'], ['ID', '#push_id', 'B']],
    'B':[[ '=', 'Expression', '#assign'], ['[', 'Expression', ']', '#array_access', 'H'], ['SimpleExpressionPrime']],
    'H':[[ '=', 'Expression', '#assign'], ['G', 'D', 'C']],
    'SimpleExpressionZegond': [['AdditiveExpressionZegond', 'C']],
    'SimpleExpressionPrime' : [['AdditiveExpressionPrime', 'C']],
    'C': [['Relop', 'AdditiveExpression', '#relop'],['EPSILON']], 
    'Relop': [['<', '#push_less_than_comparator'],['==', '#push_is_equal_comparator']], 
    'AdditiveExpression': [['Term', 'D']],
    'AdditiveExpressionPrime': [['TermPrime', 'D']],
    'AdditiveExpressionZegond': [['TermZegond', 'D']],
    'D': [['Addop', 'Term', '#add_or_subtract', 'D'],['EPSILON']], 
    'Addop':[['+', '#push_addition_operator'],['-', '#push_subtraction_operator']], 
    'Term': [['SignedFactor', 'G']],
    'TermPrime': [['SignedFactorPrime', 'G']],
    'TermZegond':[['SignedFactorZegond', 'G']],
    'G':[['*', 'SignedFactor', '#multiply','G'],['EPSILON']],
    'SignedFactor': [['+' , 'Factor'] , ['-' , 'Factor', '#negate'], ['Factor']],
    'SignedFactorPrime' : [['FactorPrime']],
    'SignedFactorZegond': [['+', 'Factor'] , ['-', 'Factor', '#negate'] , ['FactorZegond']],
    'Factor':[['(', 'Expression', ')'], ['ID', '#push_id','VarCallPrime'], ['NUM', '#push_number']],
    'VarCallPrime':[['#start_function_call', '(', 'Args', ')', '#function_call'], ['VarPrime']],
    'VarPrime':[['[', 'Expression', ']', '#array_access'],['EPSILON']], 
    'FactorPrime':[['#start_function_call' ,'(', 'Args', ')' ,'#function_call'],['EPSILON']],  
    'FactorZegond': [['(', 'Expression', ')'], ['NUM', '#push_number']],
    'Args': [['ArgList'],['EPSILON']], 
    'ArgList': [['Expression', 'ArgListPrime']],
    'ArgListPrime': [[',', 'Expression', 'ArgListPrime'],['EPSILON']]

} 

predict = {
    'Program':[['int','void','$']] ,
    'DeclarationList':[['int','void'],['ID',';','NUM','(','{','}','break','if','while','return','$']] ,
    'Declaration': [['int','void']] ,
    'DeclarationInitial' : [['int','void']] ,
    'DeclarationPrime' : [ ['('],[';','[']],
    'VarDeclarationPrime' : [[';'],['[']],
    'FunDeclarationPrime' : [['(']],
    'TypeSpecifier': [['int'],['void']] ,
    'Params': [['int'],['void']] ,
    'ParamList': [[','],[')']],#16
    'Param': [['int','void']] ,
    'ParamPrime': [['['],[')', ',']],#19
    'CompoundStmt': [['{']],#20
    'StatementList' : [['ID',';','NUM','(','{','break','if','while','return','+','-'],['}']],#22
    'Statement' : [['ID',';','NUM','(','break','+','-'], ['{'], ['if'],['while'], ['return']],#27
    'ExpressionStmt' : [['ID','NUM','(','+','-'],['break'],[';']],#30
    'SelectionStmt' : [['if']],#31
    'IterationStmt' :[['while']],#32
    'ReturnStmt' :[['return']],
    'ReturnStmtPrime': [[';'],['ID','NUM','(','+','-']],#35
    'Expression': [['NUM','(','+','-'],['ID']],#37
    'B':[['='],['['],[';',']','(',')',',','<','==','+','-','*']],#40
    'H':[['='],[';',']',')',',','<','==','+','-','*']],#42
    'SimpleExpressionZegond': [['NUM','(','+','-']],
    'SimpleExpressionPrime' : [[';',']','(',')',',','<','==','+','-','*']],#44
    'C': [['<','=='],[';',']',')',',']], 
    'Relop': [['<'],['==']],#48
    'AdditiveExpression': [['ID','NUM','(','+','-']], 
    'AdditiveExpressionPrime': [[';',']','(',')',',','<','==','+','-','*']],
    'AdditiveExpressionZegond': [['NUM','(','+','-']],#51
    'D': [['+','-'], [';',']',')',',','<','==']],
    'Addop': [['+'],['-']],#55
    'Term': [['ID','NUM','(','+','-']],
    'TermPrime': [[';',']','(',')',',','<','==','+','-','*']],
    'TermZegond':[['NUM','(','+','-']],#58
    'G': [['*'],[';',']',')',',','<','==','+','-']], #60
    'SignedFactor': [['+'] , ['-'] , ['ID','NUM','(']],#63
    'SignedFactorPrime' : [[';',']','(',')',',','<','==','+','-','*']],
    'SignedFactorZegond' : [['+'] , ['-'] , ['NUM','(']],#67
    'Factor':[['('],['ID'],['NUM']],#70
    'VarCallPrime':[['('], [';','[',']',')',',','<','==','+','-','*']],#72
    'VarPrime':[['['],[';',']',')',',','<','==','+','-','*']],#74
    'FactorPrime':[['('],[';',']',')',',','<','==','+','-','*']],#76
    'FactorZegond':[['('],['NUM']],#78
    'Args': [['ID','NUM','('],[')']],#80 
    'ArgList':[['ID','NUM','(']], #81
    'ArgListPrime': [[','],[')']]#83
} 


first = {
    'Program':['int','void','EPSILON'] ,
    'DeclarationList':['int','void','EPSILON'] ,
    'Declaration': ['int','void'] ,
    'DeclarationInitial' : ['int','void'] ,
    'DeclarationPrime' : [';','[','('],
    'VarDeclarationPrime' : [';','['],
    'FunDeclarationPrime' : ['('],
    'TypeSpecifier': ['int','void'] ,
    'Params': ['int','void'] ,
    'ParamList': [',','EPSILON'],
    'Param': ['int','void'] ,
    'ParamPrime': ['[','EPSILON'],
    'CompoundStmt': ['{'],
    'StatementList' : ['ID',';','NUM','(','{','break','if','while','return','EPSILON'],
    'Statement' : ['ID',';','NUM','(','{','break','if','while', 'return'],
    'ExpressionStmt' : ['ID',';','NUM','(','break'],
    'SelectionStmt' : ['if'],
    'IterationStmt' :['while'],
    'ReturnStmt' :['return'],
    'ReturnStmtPrime': ['ID',';','NUM','(','+','-'],
    'Expression': ['ID','NUM','(','+','-'],
    'B':['[','(','=','<','==','+','-','*','EPSILON'],
    'H':['=','<','==','+','-','*','EPSILON'],
    'SimpleExpressionZegond': ['NUM','(','+','-'],
    'SimpleExpressionPrime' : ['(','==','+','-','*','EPSILON'],
    'C': ['<','==','EPSILON'], 
    'Relop': ['<','=='],
    'AdditiveExpression': ['ID','NUM','(','+','-'], 
    'AdditiveExpressionPrime': ['(','+','-','*','EPSILON'],
    'AdditiveExpressionZegond': ['NUM','(','+','-'],
    'D': ['+','-', 'EPSILON'],
    'Addop': ['+','-'],
    'Term': ['ID','NUM','(','+','-'],
    'TermPrime': ['(','*','EPSILON'],
    'TermZegond':['NUM','(','+','-'],
    'G': ['*','EPSILON'], 
    'SignedFactor': ['ID' , 'NUM' , '(', '+', '-'],
    'SignedFactorPrime' : ['(' , 'EPSILON'],
    'SignedFactorZegond' : ['NUM' , '(', '+', '-'],
    'Factor':['ID','NUM','('], 
    'VarCallPrime':['[','(','EPSILON'],
    'VarPrime':['[','EPSILON'],
    'FactorPrime':['(','EPSILON'],
    'FactorZegond':['NUM','('], 
    'Args': ['ID','NUM','(','+','-','EPSILON'], 
    'ArgList':['ID','NUM','(','+','-'], 
    'ArgListPrime': [',','EPSILON']
} 

follow = {
    'Program':['$'] ,
    'DeclarationList':['ID',';','NUM','(','{','}','break','if','while','return','+','-','$'] ,
    'Declaration': ['int','void','ID',';','NUM','(','{','}','break','if','while','return','+','-','$'] ,
    'DeclarationInitial' : [';','[','(',')',','] ,
    'DeclarationPrime' : ['ID',';','NUM','(','int','void','{','}','break','if','while','return','+','-','$'],
    'VarDeclarationPrime' : ['ID',';','NUM','(','int','void','{','}','break','if','while','return','+','-','$'],
    'FunDeclarationPrime' : ['ID',';','NUM','(','int','void','{','}','break','if','while','return','+','-','$'],
    'TypeSpecifier': ['ID'] ,
    'Params': [')'] ,
    'ParamList': [')'],
    'Param': [')',','] ,
    'ParamPrime': [')',','],
    'CompoundStmt': ['ID',';','NUM','(','int','void','{','}','break','if','else','while','return','+','-','$'],
    'StatementList' : ['}'],
    'Statement' : ['ID',';','NUM','(','{','}','break','if','else','while','return','+','-'],
    'ExpressionStmt' : ['ID',';','NUM','(','{','}','break','if','else','while','return','+','-'],
    'SelectionStmt' : ['ID',';','NUM','(','{','}','break','if','else','while','return','+','-'],
    'IterationStmt' :['ID',';','NUM','(','{','}','break','if','else','while','return','+','-'],
    'ReturnStmt' :['ID',';','NUM','(','{','}','break','if','else','while','return','+','-'],
    'ReturnStmtPrime': ['ID',';','NUM','(','{','}','break','if','else','while','return','+','-'],
    'Expression': [';',']',')',','],
    'B':[';',']',')',','],
    'H':[';',']',')',','],
    'SimpleExpressionZegond': [';',']',')',','],
    'SimpleExpressionPrime' : [';',']',')',','],
    'C': [';',']',')',','],
    'Relop': ['ID','NUM','(','+','-'],
    'AdditiveExpression': [';',']',')',','],
    'AdditiveExpressionPrime': [';',']',')',',','<','=='],
    'AdditiveExpressionZegond': [';',']',')',',','<','=='],
    'D': [';',']',')',',','<','=='],
    'Addop': ['ID','NUM','(','+','-'],
    'Term': [';',']',')',',','<','==','+','-'],
    'TermPrime': [';',']',')',',','<','==','+','-'],
    'TermZegond':[';',']',')',',','<','==','+','-'],
    'G': [';',']',')',',','<','==','+','-'],
    'SignedFactor': [';',']',')',',','<','==','+','-','*'],
    'SignedFactorPrime' : [';',']',')',',','<','==','+','-','*'],
    'SignedFactorZegond' : [';',']',')',',','<','==','+','-','*'],
    'Factor':[';',']',')',',','<','==','+','-','*'],
    'VarCallPrime':[';',']',')',',','<','==','+','-','*'],
    'VarPrime':[';',']',')',',','<','==','+','-','*'],
    'FactorPrime':[';',']',')',',','<','==','+','-','*'],
    'FactorZegond':[';',']',')',',','<','==','+','-','*'],
    'Args': [')'], 
    'ArgList':[')'], 
    'ArgListPrime': [')']
} 

def find_all_terminal():
    my_list = []
    for i in first:
        my_list=list(my_list.union(first[i]))
    for i in follow:
        my_list=list(my_list.union(follow[i]))

    return my_list
                     
def get_keys(data):
    return list(data.keys())

KEYWORDS = ["if", "else", "void", "int", "while", "break","return"]

class LL1Parser:
    def __init__(self):
        self.syntax_errors = []
        self.root = Node('Program')
        self.scanner = scanner('input.txt')
        self.token_type = ''
        self.token = ''
        self.pre_token = ''
        self.pre_token_type = ''
        self.pre_top_of_stack = ''
        self.pre_line_number = 0
        self.line_number = 0
        self.non_terminals = get_keys(grammar)
        #self.code_gen =  CodeGenerator()
        #self.code_generator = CodeGenerator()
        #self.unexpected_EOF = False
        
    def is_non_terminal(self , word):
            if word in self.non_terminals:
                return True
            else:
                return False

    def get_next_token(self, top_of_stack):
        self.pre_token = self.token
        self.pre_token_type = self.token_type
        self.pre_top_of_stack = top_of_stack
        self.pre_line_number = self.line_number
        while True:
            self.token_type , self.token , Error, self.line_number = self.scanner.get_next_token()
            if self.token_type != 'WHITESPACE' and self.token_type != 'COMMENT' and self.token_type != 'Error':
                break
        #print('--------------------')
        #print('token: ' + self.token + '    line number: ' + str(self.line_number+1))
            
    def run_parser(self):
        self.get_next_token('')
        #print('1:',self.token,'---------------',self.token_type)
        self.parse()

    def eof_reached(self):
        if self.token == '$':
            return True
        else:
            return False
        
    def LL1table(self,top_of_stack,token,token_type):
        for i in range(len(predict[top_of_stack])):
            if token_type in predict[top_of_stack][i] or token in predict[top_of_stack][i]:
                return grammar[top_of_stack][i]
            
        if 'EPSILON' not in first[top_of_stack]:
            for x in follow[top_of_stack]:
                if x not in first[top_of_stack]:
                    return 'sync'
                
        return None

    def parse(self):
        stack = []
        self.root = Node('Program')
        stack = [('Program', None)]
        
        
        while stack:
            # top_of_stack = stack.pop()
            # self.root = Node(top_of_stack)
            top_of_stack , parent = stack.pop()
            #call code generator:
            if top_of_stack.startswith('#'):
                print(top_of_stack + ' ' + self.pre_token + ' ' + self.pre_token_type)
                #self.code_gen.generate_code(top_of_stack[1:] , self.token)
                generate_code(action= top_of_stack , label= self.pre_token)
                # if self.pre_token_type in ['NUM' , 'ID'] and self.pre_top_of_stack == self.pre_token:
                #     print('1: ' + top_of_stack + ' ' + self.pre_token + ' ' + self.pre_token_type)
                #     generate_code(action= top_of_stack[1:] , label= self.pre_token)
                # else:
                #     print('2: ' + top_of_stack + ' ' + self.pre_token + ' ' + self.pre_token_type)
                #     generate_code(action= top_of_stack[1:] , label= self.pre_token_type)
                continue
            #print('top_of_stack: ' + top_of_stack)
            current_node = Node(top_of_stack)
            current_node.parent = parent
            if parent:
                current_node.parent = parent
            else:
                self.root = current_node
            if top_of_stack == 'EPSILON':
                current_node.name = 'epsilon'
                continue


            #non terminal:
            if self.is_non_terminal(top_of_stack):
                action = self.LL1table(top_of_stack, self.token, self.token_type)

                if self.token == '$' and top_of_stack != 'DeclarationList':
                    #handle Unexpected EOF
                    # print('-------- unexpected EOF ---------')
                    # print('top of stack: ' + str(top_of_stack))
                    # print('parent: ' + str(parent))
                    # print('token: ' + self.token)
                    # print('token type: ' + self.token_type)
                    # print(stack)
                    self.syntax_errors.append('#' + str(self.line_number + 1) + ' : syntax error, Unexpected EOF')
                    #print('#' + str(self.line_number + 1) + ' : Unexpected EOF')
                    current_node.parent = None
                    break

                elif action == 'sync':
                    #handle missing error
                    self.syntax_errors.append('#' + str(self.line_number + 1) + ' : syntax error, missing ' + str(top_of_stack))
                    current_node.parent = None
                    #print('#' + str(self.line_number + 1) + ' : syntax error, missing ' + str(top_of_stack))
                    
                elif action == None:
                    #handle illegal error
                    if self.token_type in ['ID' , 'NUM']:
                        self.syntax_errors.append('#' + str(self.line_number + 1) + ' : syntax error, illegal ' + str(self.token_type))
                    else:
                        self.syntax_errors.append('#' + str(self.line_number + 1) + ' : syntax error, illegal ' + str(self.token))
                    # print('#' + str(self.line_number + 1) + ' : syntax error, illegal ' + str(top_of_stack))
                    stack.append((top_of_stack , parent))
                    current_node.parent = None
                    self.get_next_token(top_of_stack)
                    


                else:
                    #non terminal matched:
                    #push to stack
                    for part in reversed(action):
                        stack.append((part , current_node))
                        #print('pushing ' + part + ' to stack')
                    #add to parse tree
                    # for part in (action):
                    #     Node(part , current_node)
            
            #terminal:
            else:
                current_node.parent = None
                if top_of_stack in ['NUM' , 'ID'] and self.token_type == top_of_stack:
                    #add to parse tree
                    Node('(' + str(self.token_type) + ', ' + str(self.token) + ')' , parent)
                    self.get_next_token(top_of_stack)
                
                elif (top_of_stack in KEYWORDS or (top_of_stack == '==' or self.scanner.get_token_type(top_of_stack) == 'SYMBOL')) \
                      and self.token == top_of_stack:
                    Node('(' + str(self.token_type) + ', ' + str(self.token) + ')' , parent)
                    self.get_next_token(top_of_stack)
                    #print('currect')
                
                elif top_of_stack == '$':
                    # print('------- EOF -------')
                    # print('top of stack: ' + str(top_of_stack))
                    # print('parent: ' + str(parent))
                    # print('token: ' + self.token)
                    # print('token type: ' + self.token_type)
                    # print(stack)
                    Node('$' , parent)
                    break

                else:
                    #missing error:
                    # print('top of stack: ' + str(top_of_stack))
                    # print('parent: ' + str(parent))
                    # print('token: ' + self.token)
                    # print('token type: ' + self.token_type)
                    # print(stack)
                    current_node.parent = None
                    self.syntax_errors.append('#' + str(self.line_number + 1) + ' : syntax error, missing ' + str(top_of_stack))
                    #print('#' + str(self.line_number + 1) + ' : syntax error, missing ' + str(top_of_stack))


    def write_tree(self):
        with open('parse_tree.txt', 'w', encoding='utf-8') as f:
            for pre, fill, node in RenderTree(self.root):
                f.write("%s%s\n" % (pre, node.name))

    def write_syntax_errors(self):
        input = open('syntax_errors.txt','w')
        if len(self.syntax_errors)== 0:
            input.write('There is no syntax error.')
        else: 
            for i in self.syntax_errors:
                input.write(str(i+'\n'))

    def write_output(self):
        output_file = open(file='output.txt', mode='w', encoding='utf-8')
        if 1 == 2:
            output_file.write("The code has not been generated.")
        else:
            for line_number, code in program_block.items():
                print("%s\t%s" % (line_number, code))
                output_file.write("%s\t%s\n" % (line_number, code))
                

    # 'Program': [['DeclarationList','$']],
    # 'DeclarationList' : [['Declaration', 'DeclarationList'],['EPSILON']], 
    # 'Declaration' : [['DeclarationInitial',  'DeclarationPrime']],
    # 'DeclarationInitial' : [['TypeSpecifier', '#push_type' , 'ID', '#push']],
    # 'DeclarationPrime' : [['#start_function' ,'FunDeclarationPrime'], ['VarDeclarationPrime']],
    # 'VarDeclarationPrime' : [['#variable_definition',';'],['[', 'NUM' , '#push' , '#define_array', ']', ';']], 
    # 'FunDeclarationPrime' : [ ['(', 'Params', ')', '#define_function', 'CompoundStmt', '#END_SCOPE', '#end_function']],
    # 'TypeSpecifier': [['int'], ['void']],
    # 'Params': [['int', '#push', 'ID', '#push', 'ParamPrime', '#add_param', 'ParamList'], ['void']],
    # 'ParamList': [[',', 'Param', 'ParamList'], ['EPSILON']],
    # 'Param': [ ['DeclarationInitial', 'ParamPrime', '#add_param']],
    # 'ParamPrime': [['[', ']', '#push_array_input_type'],['EPSILON', '#push_normal_input_type']] ,
    # 'CompoundStmt': [['{' ,'DeclarationList', 'StatementList', '}']],
    # 'StatementList' :[[ 'Statement', 'StatementList'],['EPSILON']],  
    # 'Statement' : [['ExpressionStmt'], ['CompoundStmt'], ['SelectionStmt'], ['IterationStmt' ],['ReturnStmt']],
    # 'ExpressionStmt' : [['Expression', '#pop',';'], ['break', '#break',';'], [';']],
    # 'SelectionStmt' : [['if', '(', 'Expression', '#if', ')', 'Statement', 'else', '#else', 'Statement', '#endif']],
    # 'IterationStmt' :[[ 'while', '(', '#start_while', 'Expression', ')', '#while_condition', 'Statement', '#endwhile']], 
    # 'ReturnStmt' :[['return', 'ReturnStmtPrime']],
    # 'ReturnStmtPrime':[['#return' ,';'],['Expression', '#return_value', ';']],
    # 'Expression': [['SimpleExpressionZegond'], ['ID', '#push_id', 'B']],
    # 'B':[[ '=', 'Expression', '#assign'], ['[', 'Expression', ']', '#array_access', 'H'], ['SimpleExpressionPrime']],
    # 'H':[[ '=', 'Expression', '#assign'], ['G', 'D', 'C']],
    # 'SimpleExpressionZegond': [['AdditiveExpressionZegond', 'C']],
    # 'SimpleExpressionPrime' : [['AdditiveExpressionPrime', 'C']],
    # 'C': [['Relop', 'AdditiveExpression', '#relop'],['EPSILON']], 
    # 'Relop': [['<', '#push_less_than_comparator'],['==', '#push_is_equal_comparator']], 
    # 'AdditiveExpression': [['Term', 'D']],
    # 'AdditiveExpressionPrime': [['TermPrime', 'D']],
    # 'AdditiveExpressionZegond': [['TermZegond', 'D']],
    # 'D': [['Addop', 'Term', '#add_or_subtract', 'D'],['EPSILON']], 
    # 'Addop':[['+', '#push_addition_operator'],['-', '#push_subtraction_operator']], 
    # 'Term': [['SignedFactor', 'G']],
    # 'TermPrime': [['SignedFactorPrime', 'G']],
    # 'TermZegond':[['SignedFactorZegond', 'G']],
    # 'G':[['*', 'SignedFactor', '#multiply','G'],['EPSILON']],
    # 'SignedFactor': [['+' , 'Factor'] , ['-' , 'Factor', '#negate'], ['Factor']],
    # 'SignedFactorPrime' : [['FactorPrime']],
    # 'SignedFactorZegond': [['+', 'Factor'] , ['-', 'Factor', '#negate'] , ['FactorZegond']],
    # 'Factor':[['(', 'Expression', ')'], ['ID', '#push_id','VarCallPrime'], ['NUM', '#push_number']],
    # 'VarCallPrime':[['#start_function_call', '(', 'Args', ')', '#function_call'], ['VarPrime']],
    # 'VarPrime':[['[', 'Expression', ']', '#array_access'],['EPSILON']], 
    # 'FactorPrime':[['#start_function_call' ,'(', 'Args', ')' ,'#function_call'],['EPSILON']],  
    # 'FactorZegond': [['(', 'Expression', ')'], ['NUM', '#push_number']],
    # 'Args': [['ArgList'],['EPSILON']], 
    # 'ArgList': [['Expression', 'ArgListPrime']],
    # 'ArgListPrime': [[',', 'Expression', 'ArgListPrime'],['EPSILON']]
                



    # 'Program': [['DeclarationList','$']],
    # 'DeclarationList' : [['Declaration', 'DeclarationList'],['EPSILON']], 
    # 'Declaration' : [['DeclarationInitial',  'DeclarationPrime']],
    # 'DeclarationInitial' : [['TypeSpecifier', '#declare_pid' , 'ID', '#push']],
    # 'DeclarationPrime' : [['#label','#declare_func' , '#increase_scope','FunDeclarationPrime', '#decrease_scope'], ['VarDeclarationPrime']],
    # 'VarDeclarationPrime' : [['#declare_var',';'],['[', '#parr_size', 'NUM', ']', '#declare_array', ';']], 
    # 'FunDeclarationPrime' : [ ['(', 'Params', ')',  'CompoundStmt', '#implicit_return']],
    # 'TypeSpecifier': [['#ptype_int','int'], ['#ptype_void','void']],
    # 'Params': [['#ptype_int','int', '#push', '#declare_pid', 'ID', 'ParamPrime', 'ParamList'], ['void']],
    # 'ParamList': [[',', 'Param', 'ParamList'], ['EPSILON']],
    # 'Param': [ ['DeclarationInitial', 'ParamPrime']],
    # 'ParamPrime': [['[', ']', '#declare_pointer_param'],['EPSILON', '#declare_var_param']] ,
    # 'CompoundStmt': [['{' ,'DeclarationList', 'StatementList', '}']],
    # 'StatementList' :[[ 'Statement', 'StatementList'],['EPSILON']],  
    # 'Statement' : [['ExpressionStmt'], ['CompoundStmt'], ['SelectionStmt'], ['IterationStmt' ],['ReturnStmt']],
    # 'ExpressionStmt' : [['Expression', '#pop',';'], ['break', '#break_jump',';'], [';']],
    # 'SelectionStmt' : [['if', '(', 'Expression', ')','#save', '#increase_scope', 'Statement', '#decrease_scope', 'else', '#else', 'Statement', '#endif']],
    # 'IterationStmt' :[[ 'while', '(', '#start_while', 'Expression', ')', '#while_condition', 'Statement', '#endwhile']], 
    # 'ReturnStmt' :[['return', 'ReturnStmtPrime']],
    # 'ReturnStmtPrime':[['#return' ,';'],['Expression', '#return_value', ';']],
    # 'Expression': [['SimpleExpressionZegond'], ['ID', '#push_id', 'B']],
    # 'B':[[ '=', 'Expression', '#assign'], ['[', 'Expression', ']', '#array_access', 'H'], ['SimpleExpressionPrime']],
    # 'H':[[ '=', 'Expression', '#assign'], ['G', 'D', 'C']],
    # 'SimpleExpressionZegond': [['AdditiveExpressionZegond', 'C']],
    # 'SimpleExpressionPrime' : [['AdditiveExpressionPrime', 'C']],
    # 'C': [['Relop', 'AdditiveExpression', '#relop'],['EPSILON']], 
    # 'Relop': [['<', '#push_less_than_comparator'],['==', '#push_is_equal_comparator']], 
    # 'AdditiveExpression': [['Term', 'D']],
    # 'AdditiveExpressionPrime': [['TermPrime', 'D']],
    # 'AdditiveExpressionZegond': [['TermZegond', 'D']],
    # 'D': [['Addop', 'Term', '#add_or_subtract', 'D'],['EPSILON']], 
    # 'Addop':[['+', '#push_addition_operator'],['-', '#push_subtraction_operator']], 
    # 'Term': [['SignedFactor', 'G']],
    # 'TermPrime': [['SignedFactorPrime', 'G']],
    # 'TermZegond':[['SignedFactorZegond', 'G']],
    # 'G':[['*', 'SignedFactor', '#multiply','G'],['EPSILON']],
    # 'SignedFactor': [['+' , 'Factor'] , ['-' , 'Factor', '#negate'], ['Factor']],
    # 'SignedFactorPrime' : [['FactorPrime']],
    # 'SignedFactorZegond': [['+', 'Factor'] , ['-', 'Factor', '#negate'] , ['FactorZegond']],
    # 'Factor':[['(', 'Expression', ')'], ['ID', '#push_id','VarCallPrime'], ['NUM', '#push_number']],
    # 'VarCallPrime':[['#start_function_call', '(', 'Args', ')', '#function_call'], ['VarPrime']],
    # 'VarPrime':[['[', 'Expression', ']', '#array_access'],['EPSILON']], 
    # 'FactorPrime':[['#start_function_call' ,'(', 'Args', ')' ,'#function_call'],['EPSILON']],  
    # 'FactorZegond': [['(', 'Expression', ')'], ['NUM', '#push_number']],
    # 'Args': [['ArgList'],['EPSILON']], 
    # 'ArgList': [['Expression', 'ArgListPrime']],
    # 'ArgListPrime': [[',', 'Expression', 'ArgListPrime'],['EPSILON']]

