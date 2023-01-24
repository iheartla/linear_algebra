from iheartla.la_grammar.LA_ebnf import *
import regex as re
from textwrap import dedent


# rules that contain ';' are: params_separator, description, separator, assignment
RULE_RE = re.compile(
        dedent(r'''(?<=\n)
            (?P<name>[a-z0-9A-Z_]+)(::(?P<class>[^:\n=();]*))?[ \t]*\n
            [ \t]*=[ \t]*\n     
            (?P<body>[^;]*)
            [ \t]*;[ \t]*\n                                            
        '''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# keywords definition line
KEYWORDS_LINE_RE = re.compile(
        dedent(r'''(?<=\n)
            (?P<name>[a-z0-9A-Z_]+)
            [ \t]*=[ \t]* 
            (?P<content>[^;]*)
            [ \t]*;[ \t]*\n                                            
        '''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )
# keywords: /content/
KEYWORDS_CONTENT_RE = re.compile(
        dedent(r'''/(?P<content>[^;/\/]*)/'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# annotation for rules:
ANNOTATE_RE = re.compile(
        dedent(r'''(?<=[ *=|{(])[a-zA-Z_+]*:'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# command in grammar: start with @
COMMAND_RE = re.compile(
        dedent(r'''(?<=\n)[ \t]*@[^\n]*\n'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# comment in grammar: start with #
COMMENT_RE = re.compile(
        dedent(r'''(?<=\n)[ \t]*\#[^\n]*\n'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# curly brace {name}+
INTERNAL_CURLY_PLUS_RE = re.compile(
        dedent(r'''{(?P<name>[a-zA-Z_]*)}\+'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# curly brace {name}
INTERNAL_CURLY_RE = re.compile(
        dedent(r'''{(?P<name>[a-zA-Z_]*)}'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# squre brace [name]
INTERNAL_SQUARE_RE = re.compile(
        dedent(r'''\[(?P<name>[a-zA-Z_]*)\]'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# curly brace {name}+
OUTER_CURLY_PLUS_RE = re.compile(
        dedent(r'''{(?P<name>[^{}]*)}\+'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# curly brace {name}
OUTER_CURLY_RE = re.compile(
        dedent(r'''{(?P<name>[^{}]*)}'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# squre brace [name]
OUTER_SQUARE_RE = re.compile(
        dedent(r'''\[(?P<name>[^{}\[\]]*)\]'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

# regular expression in TatSu: /name/
REGULAR_RE = re.compile(
        dedent(r'''\/(?P<name>[^\/]*)\/'''),
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

unicode_symbol = []

special_symbol = ['∂', '𝕕', '∑', '∈', 'Δ', '∇', '⊂', '#', 'ℝ', 'ℤ', '±']

mapping_dict = {
    """/\(/""" : """'('""",
    """/\[/""" : """'['""",
}

def process_multi_line(result):
    new_result = result
    for m in RULE_RE.finditer(result):
        # print(m.group())
        body = m.group('body')
        new_body = body
        for annotate in ANNOTATE_RE.finditer(body):
            # print(annotate.group())
            new_body = new_body.replace(annotate.group(), '')
        # curly brace
        new_body = process_curly_brace(new_body)
        # square brace
        new_body = process_square_brace(new_body)
        # final result
        new_result = new_result.replace(m.group(), "{} ::= {}".format(m.group('name'), new_body.strip()))
    return new_result


def process_square_brace(result):
    # internal [name]
    new_result = result
    for curly in INTERNAL_SQUARE_RE.finditer(result):
        new_result = new_result.replace(curly.group(), '({})?'.format(curly.group('name')))
    # outer [name]
    found = True
    while found:
        found = False
        for curly in OUTER_SQUARE_RE.finditer(result):
            new_result = new_result.replace(curly.group(), '({})?'.format(curly.group('name')))
            found = True
            break
        result = new_result
    return new_result

def process_curly_brace(result):
    # internal {name}+
    new_result = result
    for curly in INTERNAL_CURLY_PLUS_RE.finditer(result):
        new_result = new_result.replace(curly.group(), '({})+'.format(curly.group('name')))
    # internal {name}
    result = new_result
    for curly in INTERNAL_CURLY_RE.finditer(result):
        new_result = new_result.replace(curly.group(), '({})*'.format(curly.group('name')))
    # outer {name}+
    result = new_result
    found = True
    while found:
        found = False
        for curly in OUTER_CURLY_PLUS_RE.finditer(result):
            new_result = new_result.replace(curly.group(), '({})+'.format(curly.group('name')))
            found = True
            break
        result = new_result
    # outer {name}
    found = True
    while found:
        found = False
        for curly in OUTER_CURLY_RE.finditer(result):
            new_result = new_result.replace(curly.group(), '({})*'.format(curly.group('name')))
            found = True
            break
        result = new_result
    return new_result

def process_single_line(result):
    # ; in a single line
    new_result = result
    for key_line in KEYWORDS_LINE_RE.finditer(result):
        content = key_line.group('content')
        new_content = content
        for key_content in KEYWORDS_CONTENT_RE.finditer(content):
            new_content = new_content.replace(key_content.group(), key_content.group('content'))
        # print(key_line.group())
        new_result = new_result.replace(key_line.group(),
                                        "{} ::= {}\n".format(key_line.group('name'), new_content.strip()))
    return new_result

def process_mapping_dict(result):
    for k,v in mapping_dict.items():
        result = result.replace(k, v)
    return result

def transform_ebnf(origin):
    result = origin
    for m in COMMAND_RE.finditer(origin):
        result = result.replace(m.group(), '')
    for m in COMMENT_RE.finditer(origin):
        result = result.replace(m.group(), '')
    result = process_multi_line(result)
    result = result.replace('$', 'EOF')
    # ; in a single line
    result = process_single_line(result)
    result = process_mapping_dict(result)
    return result


if __name__ == '__main__':
    # LA = START
    result = transform_ebnf(LA)
    print(result)
