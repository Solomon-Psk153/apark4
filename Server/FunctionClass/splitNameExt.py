
def splitNameExt(name):
    
    pos = name.rfind('.')
    
    if pos == -1:
        return (name, '')
    
    return (name[:pos], name[pos:])