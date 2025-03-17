import copy

def update(d1,d2,skip):
    # update d1 with d2, skipping keys in skip
    d3 = {k:v for k,v in d2.items() if k not in skip}
    d1.update(d3)    

def cupdate(c1,c2,skip):
    # update c1 with c2, skipping keys in skip
    # c1, c2 are classes
    for key, value in c2.__dict__.items():
        if not key.startswith('__'):
            if key not in skip:
                setattr(c1, key, value)
    
def crupdate(_A, _params): 
    # classes though, so this is a shallow/deep/mixed copy
    def _update(A,B):
        # if isinstance(B, dict):
        #     for key, value in B.items():
        #         if not key.startswith('__'):
        #             if key in A.keys():
        #                 _update(A[key], value)
        #             else:
        #                 setattr(A, key, value)
                        
        if isinstance(B, list) and isinstance(A, list):
            for i in range(len(B)):
                if i < len(A):
                    if type(A[i]) not in [str, int, float, bool]:
                        _update(A[i], B[i])
                    else:  
                        A[i] = B[i]
                else:
                    if type(A[-1]) not in [str, int, float, bool]:
                        A[i] = copy.deepcopy(A[-1])
                        _update(A[i], B[i])
                    else:  
                        A[i] = B[i]
                    
        elif hasattr(B, '__dict__'):
            for key, value in B.__dict__.items():
                if not key.startswith('__'):
                    if key in A.__dict__.keys() and type(value) not in [str, int, float, bool]:
                        _update(A.__dict__[key], value)
                    else:
                        setattr(A, key, value)
        else:
            raise ValueError(f'Cannot update {A} with {B}')
                    
    _update(_A, _params)

def pretty(d, indent=0, out=[]):
    for key, value in d.items():
      out += ('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         out += ('\t' * (indent+1) + str(value))
    return ''.join(out)
    
def internal_update(d, u):
    for k, v in u.items():
        if isinstance(d, list):
            for i in range(len(d)):
                d[i] = internal_update(d[i], u)
        elif k in d.keys():
            d[k] = v
        else:
            for kd in d.keys():
                d[kd] = internal_update(d[kd], u)
    return d
    
def select(d,i, k):
    d2 = copy.deepcopy(d)
    
    dc = d2
    for key in k[:-1]:
        dc = dc[key][0]
    dc = {k[-1]:[dc[k[-1]][i],]} # dc is now the dictionary we want to keep
    
    d2 = internal_update(d2, dc)
    return d2

def cselect(c,u,k):
    c2 = copy.deepcopy(c)
    c2.__dict__[k] = [u,]
    return c2

def cprint(c,level=0):
    if isinstance(c, dict):
        return '\n' + '\n'.join(['\t'*level + f'{key}={cprint(value, level+1)}' for key, value in c.items()])
    elif isinstance(c, list):
        return '\n' + '\n'.join(['\t'*level + cprint(value, level+1) for value in c])
    elif hasattr(c, '__dict__'):
        return '\n' + '\n'.join(['\t'*level + f'{key}:{cprint(value, level+1)}' for key, value in c.__dict__.items() if not key.startswith('__')])
    else:
        return str(c)
    
    
def serialize_class(cls, file_name):
    def process_class(cls, indent_level=0):
        _indent = "    "
        indent = _indent * indent_level
        _name = cls.__name__ if hasattr(cls, '__name__') else cls.__class__.__name__
        if _name.startswith('<'):
            return ''
        # class_code = f"{indent}class {_name}:\n"
        class_code = f"type('{_name}', (object,), {r'{'} \n"
        
        # Check for attributes in the class (via __annotations__ for typed attributes)
        annotations = False
        for key, value in cls.__dict__.items():
            if not key.startswith('__'):
                if hasattr(value, '__dict__'):  # Check if it's a class
                    class_code += f"{indent}'{value.__name__}':" + process_class(value, indent_level + 1)
                elif isinstance(value, list):
                    class_code += f"{indent}    '{key}':[ \\\n"
                    if hasattr(value[0], '__dict__'):
                        for i, item in enumerate(value):
                                class_code += _indent * (indent_level + 2) + process_class(item, indent_level + 2)
                                if i < len(value)-1:
                                    class_code += ", \n"
                    else:
                        for i, item in enumerate(value):
                            if isinstance(item, str):
                                item = f"'{item}'"
                            class_code += f"{indent}        {item},\n"
                    class_code += f"{indent}    ],\n"
                else:
                    if isinstance(value, str):
                        value = f"'{value}'"
                    class_code += f"{indent}    '{key}':{value},\n"

        # # Add a placeholder if the class is empty
        # if not annotations and not any(isinstance(obj, type) for obj in cls.__dict__.values()):
        #     class_code += f"{indent}    pass\n"
        
        class_code += f"{indent} {r'}'}),\n"
        
        return class_code

    # Generate code for the main class and its nested structure
    class_code = process_class(cls)

    # Write to the given .py file
    with open(file_name, 'w') as file:
        file.write(class_code)
        
        
import socket

def check_wifi(host="www.google.com", port=80, timeout=3):
    """
    Checks if a Wi-Fi connection is available by attempting to connect to a host.
    
    Args:
        host (str, optional): The hostname to connect to. Defaults to "www.google.com".
        port (int, optional): The port number to connect to. Defaults to 80.
        timeout (int, optional): Timeout in seconds for the connection attempt. Defaults to 3.
    
    Returns:
        bool: True if a connection is established, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False