=======
minbool
=======

`minbool` is a small library for minimizing boolean expressions. It does this
using the the Quine-McCluskey algorithm.

Simplify an Expression
======================

::

    >>> import minbool
    >>> result = minbool.simplify("A and not C or A and C")
    >>> result
    <minbool.ASTBooleanExpression object at 0xb723606c>
    >>> result.ast()
    <_ast.Name object at 0xb722ef2c>
    >>> str(result)
    'A'

Synthesize an Expression
========================

It is sometimes useful to synthesize a boolean expression from an existing 
function::

    >>> def f(A, B, C, D):
    ...     return A if B else C or D
    ... 
    >>> result = minbool.synthesize(f, 'A', 'B', 'C', 'D')
    >>> result
    <minbool.BooleanExpression object at 0xb72361cc>
    >>> str(result)
    '(not(B) and D) or (not(B) and C) or (A and B)'

Command Line Use
================

The minbool egg installs a console script: 'simplify'::

    $ simplify A and B or A and C and not C
    (A and B)

Performance
===========

Performance is big O exponential.  In each case a truthtable is constructed, 
where the number of rows is 2**N, where N is the number of variables in the 
expression.  
