


import subprocess
import argparse



class Pattern:
    def __init__(self, pattern, type, reasons=set()):
        self.pattern = pattern
        self.reasons = set(reasons)
        self.results = []
        self.type = type
class ChatResult:
    def __init__(self, pattern, line, nick=None, username=None, t=None, hostmask=None):
        self.pattern = pattern
        self.line = line
        self.nick = nick
        self.username = username
        self.t = t
        self.hostmask = hostmask
    
    def __str__(self):
        return self.line.decode()
class JoinResult:
    def __init__(self, pattern, line, nick=None, username=None, t=None, hostmask=None):
        self.pattern = pattern
        self.line = line
        self.nick = nick
        self.username = username
        self.t = t
        self.hostmask = hostmask
    
    def __str__(self):
        return self.line.decode()

class Reason:
    def __init__(self, source_pattern=None, reason=None, result=None):
        self.source_pattern = source_pattern
        self.reason = reason
        self.result = result

def grep(pattern, haystack):
    with subprocess.Popen(["grep", '-inbR', '--line-buffered', pattern, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        proc.stdin.write(haystack)
        proc.stdin.write(b'\n')
        proc.stdin.flush()
        
        for result0 in proc.stdout:
            return True
        return False
    
def main():
    
    
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('pattern', type=str,
                       help='starting pattern to search for')
    parser.add_argument('search_path', type=str, nargs='?',
                       help='path to log(s)')
    args = parser.parse_args()
    
    
    pattern0 = Pattern(args.pattern, type="nick", reasons=[Reason(reason='initial pattern')])
    
    #{pattern_string => Pattern}
    patterns = {args.pattern: pattern0}
    
    
    tovisit = set([pattern0])
    
    
    search_path = args.search_path
    
    if search_path is None or len(search_path.strip()) == 0:
        search_path = '*'
    
    while len(tovisit):
        pattern = tovisit.pop()
        with subprocess.Popen(["grep", '-inbR', '--line-buffered', pattern.pattern, search_path], stdout=subprocess.PIPE) as proc:

            for result0 in proc.stdout:
                result = result0
                result_path,_,result = result.partition(b':')
                result_line_offset,_,result = result.partition(b':')
                result_byte_offset,_,result = result.partition(b':')
                result_date,result = result[:15], result[16:]
                
                #print(result0)
                #print (result, result[:1], result[:1] == b'*', result.endswith(b'has joined\n'))
                if result[:1] == b'*' and result.endswith(b'has joined\n'):
                    _,_,nick = result.partition(b'*\t')
                    nick,_,_ = nick.partition(b' ')
                    _,_,hostmask = result.partition(b'(')
                    hostmask,_,_ = hostmask.partition(b')')
                    ircusername,_,hostmask = hostmask.partition(b'@')
                    result = JoinResult(pattern=pattern, line=result0, nick=nick, username=ircusername, t=result_date, hostmask=hostmask)
                    
                    if pattern.type == 'nick' or pattern.type == 'hostmask':
                        pattern.results += [result]
                elif result[:1] == b'<':
                    nick,_,result = result[1:].partition(b'>')
                    
                    result = ChatResult(pattern=pattern, line=result0, nick=nick, t=result_date)
                    
                    if pattern.type == 'nick' and grep(pattern.pattern, nick):
                        pattern.results += [result]
                else:
                    print (result)








if __name__ == '__main__':
    main()

