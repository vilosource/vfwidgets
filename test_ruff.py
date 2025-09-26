# Test file with intentional issues for testing ruff
import os
import sys
unused_import = "test"

def badly_formatted_function( x,y ,z ):
    """This function has formatting issues"""
    result=x+y+z
    return  result

# Line that's way too long to test line length checking even though it's ignored in the config but let's see what happens with a really long line like this one