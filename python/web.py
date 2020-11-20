import re


def is_url(url):
    """boolean check for whether a string is a zmq url"""
    if '://' not in url:
        return False
    proto, addr = url.split('://', 1)
    if proto.lower() not in ['tcp','pgm','epgm','ipc','inproc']:
        return False
    return True


def validate_url(url):
    """validate a url for zeromq"""
    if not isinstance(url, basestring):
        raise TypeError("url must be a string, not %r"%type(url))
    url = url.lower()
    
    proto_addr = url.split('://')
    assert len(proto_addr) == 2, 'Invalid url: %r'%url
    proto, addr = proto_addr
    assert proto in ['tcp','pgm','epgm','ipc','inproc'], "Invalid protocol: %r"%proto
    
    # domain pattern adapted from http://www.regexlib.com/REDetails.aspx?regexp_id=391
    # author: Remi Sabourin
    pat = re.compile(r'^([\w\d]([\w\d\-]{0,61}[\w\d])?\.)*[\w\d]([\w\d\-]{0,61}[\w\d])?$')
    
    if proto == 'tcp':
        lis = addr.split(':')
        assert len(lis) == 2, 'Invalid url: %r'%url
        addr,s_port = lis
        try:
            port = int(s_port)
        except ValueError:
            raise AssertionError("Invalid port %r in url: %r"%(port, url))
        
        assert addr == '*' or pat.match(addr) is not None, 'Invalid url: %r'%url
        
    else:
        # only validate tcp urls currently
        pass
    
    return True


def url_path_join(*pieces):
    """Join components of url into a relative url

    Use to prevent double slash when joining subpath. This will leave the
    initial and final / in place
    """
    initial = pieces[0].startswith('/')
    final = pieces[-1].endswith('/')
    striped = [s.strip('/') for s in pieces]
    result = '/'.join(s for s in striped if s)
    if initial: result = '/' + result
    if final: result = result + '/'
    if result == '//': result = '/'
    return result


def urlize(text, trim_url_limit=None, nofollow=False):
    """Converts any URLs in text into clickable links. Works on http://,
    https:// and www. links. Links can have trailing punctuation (periods,
    commas, close-parens) and leading punctuation (opening parens) and
    it'll still do the right thing.

    If trim_url_limit is not None, the URLs in link text will be limited
    to trim_url_limit characters.

    If nofollow is True, the URLs in link text will get a rel="nofollow"
    attribute.
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None \
                         and (x[:limit] + (len(x) >=limit and '...'
                         or '')) or x
    words = _word_split_re.split(text_type(escape(text)))
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = _punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or (
                '@' not in middle and
                not middle.startswith('http://') and
                not middle.startswith('https://') and
                len(middle) > 0 and
                middle[0] in _letters + _digits and (
                    middle.endswith('.org') or
                    middle.endswith('.net') or
                    middle.endswith('.com')
                )):
                middle = '<a href="http://%s"%s>%s</a>' % (middle,
                    nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or \
               middle.startswith('https://'):
                middle = '<a href="%s"%s>%s</a>' % (middle,
                    nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and \
               not ':' in middle and _simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return u''.join(words)


# Doesn’t alter your CSS rules and selectors
# Warning: strings can be altered (ex: content: "..." )
# Warning: doesn’t remove spaces before “:” in CSS rules (ex: color :red )
def minify_css(s):
    # Removes all CSS comments
    # Removes all unnecessary spaces, tabs and line breaks
    s = s.replace(((parse.Q('/*')+parse.ANY[::-1]+parse.Q('*/')) | parse.WHITESPACE)[1:].emit(), ' ')
    # Removes all unnecessary semicolons
    s = s.replace(r'[ ;]*([^\w:*.#% -])[ ;]*', '$1')
    # Removes all unnecessary * in CSS selectors (ex: *:before { ... } )
    s = s.replace((parse.Q('*')[:1]+':'+parse.Q(' '))[:].emit(), ':')
    return s.strip()


# Warning: strings can be altered (ex: <body onload="..."> )
def minify_html(s):
    # Removes all HTML comments
    # Removes all unnecessary spaces, tabs and line breaks
    s = s.replace(((parse.Q('<!-')+parse.ANY[:]+parse.Q('->')) | parse.WHITESPACE)[1:].emit(), ' ')
    # Removes trailing spaces and slashes in tags (ex: <br />)
    s = s.replace((parse.Q(' ')+parse.ahead('<')).emit(), '')
    s = s.replace((parse.Q(' ')[:1]+parse.Q('/')[:1]+parse.ahead('>')).emit(), '')
    # Removes unnecessary closing tags (</li>, </tr>, </th>,</td> and </p> sometimes)
    s = s.replace(r'<\/(?:li|t[rhd])>|<.p> *(<[p/])|','$1$2') # case insensitive
    return s.strip()


# url quote and unquote
# escaping
# params
# html