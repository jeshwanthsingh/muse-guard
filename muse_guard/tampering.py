"""Day6 implementation: compare test-scoped AST observations under our own policy.
This does not run candidate tests or reuse the former ast-grep reference patterns.
"""
import ast
import json
from pathlib import Path

POLICY=json.loads(Path(__file__).with_name('detection_policy.json').read_text())
SIGNALS={'check_sites','unit_omissions','pytest_omissions','runtime_omissions','literal_asserts','unit_constants'}
if POLICY.get('schema')!=1 or {r['signal'] for r in POLICY['checks']}!=SIGNALS|{'syntax'} or len(POLICY['checks'])!=7:
    raise ValueError('Detection policy is incomplete')


def literal(node):
    try:return True,ast.literal_eval(node)
    except (ValueError,TypeError,SyntaxError,RecursionError):return False,None


def fixed_truth(node):
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.Not):
        value=fixed_truth(node.operand)
        return None if value is None else not value
    if isinstance(node,ast.Compare) and len(node.ops)==len(node.comparators)==1 and isinstance(node.ops[0],ast.Eq):
        left,a=literal(node.left);right,b=literal(node.comparators[0])
        return a==b if left and right else None
    known,value=literal(node)
    return bool(value) if known else None


def dotted(node):
    if isinstance(node,ast.Name):return node.id
    if isinstance(node,ast.Attribute):return dotted(node.value)+'.'+node.attr
    return ''


class SuiteShape(ast.NodeVisitor):
    def __init__(self,source):
        tree=ast.parse(source);self.scope=[];self.aliases={};self.items={key:[] for key in SIGNALS}
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for name in node.names:self.aliases[name.asname or name.name]=name.name
            if isinstance(node,ast.ImportFrom) and node.module:
                for name in node.names:self.aliases[name.asname or name.name]=node.module+'.'+name.name
        self.visit(tree)
    def add(self,signal,node):
        self.items[signal].append((tuple(self.scope),ast.dump(node,include_attributes=False)))
    def resolve(self,node):
        name=dotted(node);root,separator,tail=name.partition('.')
        return self.aliases.get(root,root)+(separator+tail if separator else '')
    def omission(self,node):
        name=self.resolve(node.func if isinstance(node,ast.Call) else node)
        if name in {'unittest.skip','unittest.skipIf','unittest.skipUnless'}:self.add('unit_omissions',node)
        elif name in {'pytest.mark.skip','pytest.mark.skipif','pytest.mark.xfail'}:self.add('pytest_omissions',node)
        elif name in {'pytest.skip','pytest.xfail'} or name.endswith('.skipTest'):self.add('runtime_omissions',node)
    def visit_ClassDef(self,node):
        self.scope.append('class:'+node.name)
        for decorator in node.decorator_list:
            if not isinstance(decorator,ast.Call):self.omission(decorator)
        self.generic_visit(node);self.scope.pop()
    def visit_FunctionDef(self,node):
        self.scope.append('test:'+node.name)
        for decorator in node.decorator_list:
            if not isinstance(decorator,ast.Call):self.omission(decorator)
        self.generic_visit(node);self.scope.pop()
    visit_AsyncFunctionDef=visit_FunctionDef
    def visit_Assert(self,node):
        self.add('check_sites',node)
        if fixed_truth(node.test) is True:self.add('literal_asserts',node)
        self.generic_visit(node)
    def visit_Call(self,node):
        name=dotted(node.func).rsplit('.',1)[-1]
        if name.startswith('assert') or (isinstance(node.func,ast.Attribute) and name=='check'):
            self.add('check_sites',node)
            constant=False
            if name in {'assertTrue','assert_'} and node.args:constant=fixed_truth(node.args[0]) is True
            if name=='assertFalse' and node.args:constant=fixed_truth(node.args[0]) is False
            if name=='assertEqual' and len(node.args)>=2:
                a,left=literal(node.args[0]);b,right=literal(node.args[1]);constant=a and b and left==right
            if constant:self.add('unit_constants',node)
        self.omission(node);self.generic_visit(node)
    def occurrences(self,signal):
        # Occurrence ordinals keep two identical predicates distinct, while scope
        # ownership prevents moving a check into another test to conceal removal.
        slots={};found=set()
        for site in self.items[signal]:
            ordinal=slots.get(site,0);slots[site]=ordinal+1;found.add((*site,ordinal))
        return found


def compare_tests(original,candidate):
    try:before=SuiteShape(original);after=SuiteShape(candidate)
    except (SyntaxError,ValueError,RecursionError):
        rule=next(r for r in POLICY['checks'] if r['signal']=='syntax')
        return [rule['id']+': '+rule['message']]
    findings=[]
    for rule in POLICY['checks']:
        if rule['signal']=='syntax':continue
        old=before.occurrences(rule['signal']);new=after.occurrences(rule['signal'])
        changes=old-new if rule['change']=='missing' else new-old
        findings.extend([rule['id']+': '+rule['message']] * len(changes))
    return findings
