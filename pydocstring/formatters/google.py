"""
Google Docstring Formatter
"""
from parso.python.tree import Class, ExprStmt, Function, KeywordStatement, Module, Name, PythonNode
from pydocstring.formatters.format_utils import (get_exception_name, get_param_info,
                                                 get_return_info, parse_existing_docstring,
                                                 safe_determine_type)


def function_docstring(parso_function: Function):
    """
    Format a google docstring for a function

    Args:
        parso_function: The function tree node

    Returns:
        str: The formatted docstring
    """
    assert isinstance(parso_function, Function)

    params = parso_function.get_params()
    docstring = "\n"

    doc = parso_function.get_doc_node()
    header, params_doc, footer = parse_existing_docstring(doc)

    if header:
        docstring += header

    if params:
        docstring += "\n\nArgs:\n"
        for param in params:
            if param.star_count == 1:
                docstring += "    *{0}: {1}\n".format(
                    param.name.value, "Variable length argument list."
                )
            elif param.star_count == 2:
                docstring += "    **{0}: {1}\n".format(
                    param.name.value, "Arbitrary keyword arguments."
                )
            else:
                name, type_, default = get_param_info(param)
                default_docstring = f"    {name} ({type_}): {default}\n"
                docstring += params_doc.get(name, "") or default_docstring

    returns = list(parso_function.iter_return_stmts())
    if returns:
        docstring += "\n\nReturns:\n"
        for ret in returns:
            docstring += "    {0}: {1}\n".format(
                *get_return_info(ret, parso_function.annotation)
            )
    elif parso_function.annotation:
        docstring += "\n\nReturns:\n"
        docstring += "    {0}: \n".format(parso_function.annotation.value)

    yields = list(parso_function.iter_yield_exprs())
    if yields:
        docstring += "\n\nYields:\n"
        for yie in yields:
            docstring += "    {0}: {1}\n".format(
                *get_return_info(yie, parso_function.annotation)
            )

    raises = list(parso_function.iter_raise_stmts())
    if raises:
        docstring += "\n\nRaises:\n"
        for exception in raises:
            docstring += "    {0}: \n".format(get_exception_name(exception))

    docstring += "\n"
    return docstring


def class_docstring(parso_class):
    """
    Format a google docstring for a class

    Only documents attributes, ``__init__`` method args can be documented on the ``__init__`` method

    Args:
        parso_class (Class): The class tree node

    Returns:
        str: The formatted docstring

    """
    assert isinstance(parso_class, Class)
    docstring = "\n"
    attribute_expressions = []

    for child in parso_class.children:
        if child.type == "suite":
            for child2 in child.children:
                if child2.type == "simple_stmt":
                    for child3 in child2.children:
                        if child3.type == "expr_stmt":
                            attribute_expressions.append(child3)

    print(attribute_expressions)
    if attribute_expressions:
        docstring += "\n\nAttributes:\n"
        for attribute in attribute_expressions:
            name = attribute.children[0].value
            code = attribute.get_rhs().get_code().strip()
            attr_type = safe_determine_type(code)
            attr_str = "    {0} ({1}): {2}\n".format(name, attr_type, code)
            docstring += attr_str

    docstring += "\n"
    return docstring


def module_docstring(parso_module):
    """
    Format a google docstring for a module

    Only documents attributes, ``__init__`` method args can be documented on the ``__init__`` method

    Args:
        parso_module (Module): The module tree node

    Returns:
        str: The formatted docstring

    """
    assert isinstance(parso_module, Module)
    docstring = "\n"
    attribute_expressions = []

    for child in parso_module.children:
        if child.type == "simple_stmt":
            for child2 in child.children:
                if child2.type == "expr_stmt":
                    attribute_expressions.append(child2)

    if attribute_expressions:
        docstring += "\n\nAttributes:\n"
        for attribute in attribute_expressions:
            name = attribute.children[0].value
            code = attribute.get_rhs().get_code().strip()
            attr_type = safe_determine_type(code)
            attr_str = "    {0} ({1}): {2}\n".format(name, attr_type, code)
            docstring += attr_str

    docstring += "\n"
    if not docstring.strip():
        docstring = "\n\nEmpty Module\n\n"
    return docstring
