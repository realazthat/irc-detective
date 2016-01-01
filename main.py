


import subprocess
import argparse
import re


class Pattern:
    def __init__(self, pattern, type, reasons=[]):
        self.pattern = pattern
        self.reasons = list(reasons)
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

def egrep(pattern, haystack):
    regex = re.compile(pattern, re.IGNORECASE)
    result = regex.search(haystack)
    
    return result != None
def grep(pattern, haystack):
    with subprocess.Popen(["grep", '-inbR', '--line-buffered', pattern, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        proc.stdin.write(haystack)
        proc.stdin.write(b'\n')
        proc.stdin.flush()
        proc.stdin.close()
        
        for result0 in proc.stdout:
        
            return True
            
        return False


class LineClassifier:

    def handle_action(self, nick, text, line, result_path, line_offset, byte_offsetresult_date):
        pass
    def handle_join(self, nick, ircusername, hostmask, line, result_date):
        pass
    def handle_quit(self, nick, ircusername, hostmask, line, result_date):
        pass
    def handle_chat(self, nick, text, line, result_date):
        pass
    def handle_unknown(self, line, result_date):
        pass

    def process(self,line):
        result = line
        result_date,result = result[:15], result[16:]
        
        #print(result0)
        #print (result, result[:1], result[:1] == b'*', result.endswith(b'has joined\n'))
        if result[:1] == b'*' and result.endswith(b'has joined\n') or result.endswith(b'has left\n'):
            _,_,nick = result.partition(b'*\t')
            nick,_,_ = nick.partition(b' ')
            _,_,hostmask = result.partition(b'(')
            hostmask,_,_ = hostmask.partition(b')')
            ircusername,_,hostmask = hostmask.partition(b'@')
            
            if result.endswith(b'has joined\n'):
                return self.handle_join(nick, ircusername, hostmask, line, result_date)
            if result.endswith(b'has quit\n'):
                return self.handle_quit(nick, ircusername, hostmask, line, result_date)
            
        elif result[:1] == b'<':
            nick,_,result = result[1:].partition(b'>')
            return self.handle_chat(nick, result[1:], line, result_date)
        elif result[:1] == b'*' and result.partition(b' ')[2].startswith(b'has quit ('):
            return
        elif result[:1] == b'*' and result.partition(b' ')[2].startswith(b'is now known as '):
            return
        elif result.startswith(b'*\tChanServ gives voice to\n'):
            #it is autovoice
            return
        elif result.startswith(b'-ChanServ-') or result.startswith(b'-NickServ-'):
            #it is a NOTICE
            return
        elif result[:1] == b'*':
            #some sort of action
            _,_,result = result.partition(b'\t')
            nick,_,result = result.partition(b' ')
            
            return self.handle_action(nick, result, line, result_date)
            
        else:
            return self.handle_unknown(line, result_date)
    

class MyLineClassifier(LineClassifier):
    def __init__(self, pattern):
        self.pattern = pattern
    def handle_action(self, nick, text, line, result_date):
        if self.pattern.type == 'nick':
            if egrep(self.pattern.pattern, nick):
                #pattern did action
                print (line)
                
            else:
                #action happened to pattern
                return

    def handle_join(self, nick, ircusername, hostmask, line, result_date):
        result = JoinResult(pattern=self.pattern, line=line, nick=nick, username=ircusername, t=result_date, hostmask=hostmask)
        
        if self.pattern.type == 'nick' or self.pattern.type == 'username' or self.pattern.type == 'hostmask':
            self.pattern.results += [result]
        
        new_patterns = []
        new_patterns += [Pattern(pattern=nick, type='nick', reasons=[Reason(self.pattern, reason="matched %s to join" % self.pattern.type, result=line)])]
        new_patterns += [Pattern(pattern=ircusername, type='username', reasons=[Reason(self.pattern, reason="matched %s to join" % self.pattern.type, result=line)])]

        def extract_ip(hostmask):
            octet = br"((\d\d\d)|(\d\d)|(\d))"
            sep = br"[\.\-]"
            regex = re.compile( b''.join([octet,sep,octet,sep,octet,sep,octet]) )
            match = regex.search(hostmask)
            if match is None:
                return None
            return match.group(0).replace(b'-', b'.')
        
        ip = extract_ip(hostmask)
        if ip is not None:
            new_patterns += [Pattern(pattern=ip, type='hostmask', reasons=[Reason(self.pattern, reason="matched %s to join" % self.pattern.type, result=line)])]
        
        def extract_domain(hostmask):
            return None
        def resolve_domain(hostmask):
            return None
        
        domain = extract_domain(hostmask)
        if domain is not None:
            ip = resolve_domain(domain)
            if ip is not None:
                new_patterns += [Pattern(pattern=ip, type='hostmask', reasons=[Reason(self.pattern, reason="matched %s to join" % self.pattern.type, result=line)])]

        return new_patterns
        
    def handle_chat(self, nick, text, line, result_date):
    
        result = ChatResult(pattern=self.pattern, line=line, nick=nick, t=result_date)
        
        if self.pattern.type == 'nick' and egrep(self.pattern.pattern, nick):
            self.pattern.results += [result]
    def handle_unknown(self, line, result_date):
        print (line)
    
def main():
    
    
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('pattern', type=str,
                       help='starting pattern to search for')
    parser.add_argument('search_path', type=str, nargs='?',
                       help='path to log(s)')
    args = parser.parse_args()
    
    
    pattern0 = Pattern(args.pattern.encode(), type="nick", reasons=[Reason(reason='initial pattern')])
    
    #{pattern_string => Pattern}
    patterns = {args.pattern: pattern0}
    
    
    tovisit = set([pattern0])
    
    
    search_path = args.search_path
    
    if search_path is None or len(search_path.strip()) == 0:
        search_path = '*'
    
    while len(tovisit):
        print ('patterns.keys():',patterns.keys())
        pattern = tovisit.pop()
        classifier = MyLineClassifier(pattern)
        with subprocess.Popen(["grep", '-inbR', '--line-buffered', pattern.pattern, search_path], stdout=subprocess.PIPE) as proc:

            for match in proc.stdout:
            
                result = match
                result_path,_,result = result.partition(b':')
                line_offset,_,result = result.partition(b':')
                byte_offset,_,result = result.partition(b':')
                
                
                new_patterns = classifier.process(result)
                
                if new_patterns is not None:
                    for new_pattern1 in new_patterns:
                        new_pattern0 = None
                        if new_pattern1.pattern not in patterns:
                            patterns[new_pattern1.pattern] = new_pattern1
                            
                            tovisit.add(new_pattern1)
                        elif new_pattern1.pattern in patterns:
                            new_pattern0 = patterns[new_pattern1.pattern]
                            new_pattern0.reasons += new_pattern1.reasons






if __name__ == '__main__':
    main()

