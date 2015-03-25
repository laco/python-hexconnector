from importlib import import_module
from logging import getLogger


logger = getLogger(__name__)


class HexConnector(dict):
    """ Hexagonal Architecture Connector

        cn = HexConnector(default_value='sample', ...)
        cn.register_adapter('sample_port', 'sample.python.module')
        cn.register_adapter('new_port', 'sample.new_port')

        cn.f_('sample_port', 'function_name', 1, 2, 3) ### args...
        cn.call_fn('new_port', 'sample_function')

        obj = cn.g_('sample_port', 'obj_name', default_value)

    """

    def __init__(self, *args, **kwargs):
        super(HexConnector, self).__init__(*args, **kwargs)
        self['_ports'] = []
        self['_initialized_ports'] = []
        self.call_stack_level = 0

    def register_adapter(self, port, module):
        def _add_mod_object(n, o):
            objkey = (port, n)
            self[objkey] = o
            return objkey, o

        def _is_obj_public(n, o):
            if n.startswith('_'):
                return False
            if hasattr(o, '__all__') and n not in getattr(o, '__all__'):
                return False
            return True

        self['_ports'].append(port)
        if isinstance(module, dict):
            return [_add_mod_object(name, obj) for name, obj in module.items()]
        else:
            _mod = import_module(module) if isinstance(module, str) else module
            _mod_public_names = (name for name in dir(_mod) if _is_obj_public(name, _mod))
            return [_add_mod_object(name, getattr(_mod, name)) for name in _mod_public_names]

    def close_all_adapters(self):
        for port in self['_initialized_ports']:
            if (port, 'close_adapter') in self:
                self.call_fn('{}.close_adapter'.format(port))

    def get_from(self, what, default=None):
        port, obj_name = self._what(what)
        return self.get((port, obj_name), default)

    def set_to(self, what, value):
        port, obj_name = self._what(what)
        self[(port, obj_name)] = value

    def call_fn(self, what, *args, **kwargs):
        """ Lazy call init_adapter then call the function """
        logger.debug('f_{0}:{1}{2}({3})'.format(
            self.call_stack_level,
            ' ' * 4 * self.call_stack_level,
            what,
            arguments_as_string(args, kwargs)))
        port, fn_name = self._what(what)
        if port not in self['_initialized_ports']:
            self._call_fn(port, 'init_adapter')
            self['_initialized_ports'].append(port)
        return self._call_fn(port, fn_name, *args, **kwargs)

    def _call_fn(self, port, fn_name, *args, **kwargs):
        _fn = self[(port, fn_name)]
        self.call_stack_level += 1
        ret = _fn(self, *args, **kwargs)
        self.call_stack_level -= 1
        return ret

    def _what(self, name):
        if '.' in name:
            port, oname = name.split('.')
        else:
            port, oname = '_', name
        return port, oname

    f_ = call_fn
    g_ = get_from
    s_ = set_to


def _argument_as_string(arg):
    def _cut_str(s, m=128):
        return s[:m] + '...' if len(s) > m else s

    if isinstance(arg, str):
        return '"{}"'.format(_cut_str(arg))
    elif isinstance(arg, int):
        return '{}'.format(str(arg))
    elif isinstance(arg, list):
        return '[{}]'.format('list:' + str(len(arg)))
    elif isinstance(arg, dict):
        return '{{}}'.format('dict:' + str(len(arg)))
    else:
        return _cut_str(str(arg))


def arguments_as_string(args, kwargs):
    ret = []
    for a in args:
        ret.append(_argument_as_string(a))
    for k, v in kwargs.items():
        ret.append('{0}={1}'.format(k, _argument_as_string(v)))
    return ', '.join(ret)
