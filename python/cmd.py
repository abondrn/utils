import inspect
import sys
import argparse
import shlex

class OptionError(Exception):
    pass


def prompt_str(prompt, regex=None, default=None, loop=True):
    return input(prompt)


def prompt_list(prompt, sep=',', loop=True):
    pass


def prompt_bool(prompt='y/n? ', default=None, loop=True):
    q = raw_input(prompt)
    while q not in ['y', 'n', 'yes', 'no', '']:
        q = raw_input(prompt)
    return q in ['y', 'yes', '']


def prompt_int(prompt, min=None, max=None, default=None, loop=True):
    pass


def prompt_choice(prompt, options, default=None, normcase=True, loop=True):
    letters = string.ascii_lowercase[:len(options)]
    
    if prompt != None:
        print (prompt)
    print ('') # indent
    for opt in zip(letters, options):
        print ('(%s) %s' % opt)
    print ('')
    
    q = raw_input()
    while q not in letters and q != '':
        print ('Please enter only letters from one of the options above, or a blank line to break the loop')
        q = raw_input()
    return q


def main(fn):
    """Call fn with command line arguments.  Used as a decorator.

    The main decorator marks the function that starts a program. For example,

    @main
    def my_run_function():
        # function body

    Use this instead of the typical __name__ == "__main__" predicate.
    """
    if inspect.stack()[1][0].f_locals['__name__'] == '__main__':
        args = sys.argv[1:] # Discard the script name from command line
        print (fn(*args)) # Call the main function
    return fn


def get_choice_opt(options, optname, allowed, default=None, normcase=False):
    string = options.get(optname, default)
    if normcase:
        string = string.lower()
    if string not in allowed:
        raise OptionError('Value for option %s must be one of %s' %
                          (optname, ', '.join(map(str, allowed))))
    return string


def get_bool_opt(options, optname, default=None):
    string = options.get(optname, default)
    if isinstance(string, bool):
        return string
    elif isinstance(string, int):
        return bool(string)
    elif not isinstance(string, basestring):
        raise OptionError('Invalid type %r for option %s; use '
                          '1/0, yes/no, true/false, on/off' % (
                          string, optname))
    elif string.lower() in ('1', 'yes', 'true', 'on'):
        return True
    elif string.lower() in ('0', 'no', 'false', 'off'):
        return False
    else:
        raise OptionError('Invalid value %r for option %s; use '
                          '1/0, yes/no, true/false, on/off' % (
                          string, optname))


def get_int_opt(options, optname, default=None):
    string = options.get(optname, default)
    try:
        return int(string)
    except TypeError:
        raise OptionError('Invalid type %r for option %s; you '
                          'must give an integer value' % (
                          string, optname))
    except ValueError:
        raise OptionError('Invalid value %r for option %s; you '
                          'must give an integer value' % (
                          string, optname))


def get_list_opt(options, optname, default=None):
    val = options.get(optname, default)
    if isinstance(val, basestring):
        return val.split()
    elif isinstance(val, (list, tuple)):
        return list(val)
    else:
        raise OptionError('Invalid type %r for option %s; you '
                          'must give a list value' % (
                          val, optname))


def proceed(prompt, allowed_chars, error_prompt=None, default=None):
    p = prompt
    while True:
        s = raw_input(p)
        p = prompt
        if not s and default:
            s = default
        if s:
            c = s[0].lower()
            if c in allowed_chars:
                break
            if error_prompt:
                p = '%c: %s\n%s' % (c, error_prompt, prompt)
    return c


def pause():
    """
    Pauses the output stream awaiting user feedback.
    """
    print ('<Press enter/return to continue>')
    raw_input()


class DefaultArguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class Arguments:
    def __init__(self, posix: bool = False, allow_abbrev: bool = False, **kwargs):
        self.parser = DefaultArguments(allow_abbrev=allow_abbrev, add_help=False, **kwargs)
        self.posix = posix

    def add_argument(self, *inputs, **kwargs):
        """ Shortcut to argparse.add_argument """
        self.parser.add_argument(*inputs, **kwargs)

    def parse_args(self, text):
        """ Shortcut to argparse.parse_args with shlex implemented """
        try:
            args = self.parser.parse_args(
                shlex.split(text if text else "", posix=self.posix)
            )
        except Exception as e:
            return (f"ArgumentError: {e}", False)

        return (args, True)
