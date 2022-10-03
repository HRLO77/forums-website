from genericpath import isfile
import re
import os
import ast
import tokenize
t
func = input('Function to replace: ')
PATTERN = r'get_post\(.*\) *(\[(([^\[\(\{:;=\+\-*/`~%@\\]+|[^\[\(\{:;=\+\-*/`~%@\\]?):?){0,3}\])?'
print(PATTERN)
file = ''
while not os.path.isfile(file):
    file = input('Enter file: ')    
    
    
file = open(file, 'r').read()
def find_next():
    m = re.search(PATTERN, file)

    match = file[m.span()[0]: m.span()[1]]
    if match.count('(') != match.count(')'):
        matched = False
        if match.count('(') > match.count(')'):
            while not matched:
                test = re.search(r'\(', match)
                match = match[0:test.span()[0]] + match[test.span()[1]:]
                matched = match.count('(') == match.count(')')
        else:
            while not matched:
                test = re.search(r'\)', match)
                match = match[0:test.span()[0]] + match[test.span()[1]:]
                matched = match.count('(') == match.count(')')
    return match, m.span()

while True:
    try:
        found = find_next()
        f = list(found[0])
        c = found[1][0]
        for i in range(7):
            f.insert(c, ' await '[i])
        file = file[:found[1][0]] + ''.join(f) + file[found[1][1]:]
        print(file)
    except Exception as e:
        print(e)
        if "'NoneType' object has no attribute 'span'" == str(e):
            break
print(file)