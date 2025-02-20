import string
alnum = set(string.ascii_letters + string.digits)

def get_between(s:str, start:str, end:str) -> str:
    s=s[s.find(start)+len(start):]
    return(s[:s.find(end)])

def remove_between(s:str, start:str, end:str) -> str:
    o=""
    w=True
    for c in s:
        if(c in start):
            w=False
        elif(c in end):
            w=True
            o+=" "
        elif(w):
            o+=c
    return(o)

def unempty(s:str) -> str:
    o=""
    for line in s.splitlines():
        if len(set(line) & alnum) > 0:
            o+=line+"\n"
    return(o)