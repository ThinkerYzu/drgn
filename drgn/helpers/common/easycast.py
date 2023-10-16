import drgn

__all__ = ('easycast',)

class easycast(object):
    '''
    Provide a simple way to cast an :class:`drgn.Object` to a :class:`drgn.Type`.

    It starts from an empty instance, and you can add a token of a
    type by getting an attribute of the same name of the token. For
    example, to add a token of type `int`, you can do `_.int`. To
    create a type of two tokens `unsigned long`, you can do
    `_.unsigned.long`. `_` is an empty instance of `easycast`.

    To make a int pointer type, you can use `_.int._`.  To make a int
    pointer pointer type, you can use `_.int._._` or `_.int.__`. To
    make a int pointer pointer.

    To cast a value to an int, you can use `_.int(1)`. To cast a value
    to an int pointer type, you can use `_.int._(1)`. To cast a value
    to an int pointer pointer type, you can use `_.int._._(1)`. To
    cast a value to an int struct foo pointer type, you can use
    `_.struct.foo._(1)`.

    You can also declare a function pointer type `int (*)(int, int)`
    by using `_.int(_._)(_.int, _.int)`. To cast a value to a function
    pointer type, you can use `_.int(_._)(_.int, _.int)(func)`.  For a
    function pointer type with no parameter, you can use
    `_.int(_._)(None)`.  There is a special case here. You can use an
    empty instance to represent a pointer `*` here, so you can use
    `_.int(_)(_.int, _.int)(func)` to represent `(int (*)(int,
    int))func`.

    To declare an int array type, you can use `_.int[10]`. To declare
    an int array without a size, you can use `_.int[None]`. To cast a
    value to an int array pointer type, you can use `_.int(_._)[10](0)` or
    just `_.int(_)[10](0)`.

    '''
    def __init__(self, token=None, predecessor=None, prog=None):
        if token and token == '_' * len(token):
            token = '*' * len(token)
            pass
        self.__token = token
        self.__predecessor = predecessor
        self.__prog = prog
        pass

    def __getattr__(self, name):
        return self.__class__(name, self, prog=self.__prog)

    def __getitem__(self, index):
        ec = self.__class__('[]', self, prog=self.__prog)
        ec.sz = index
        return ec

    # Python should translate __stringify to _easycast__stringify in
    # the class. This can reduce the chance of name conflict.
    def __stringify(self):
        tokens = []
        ec = self
        while ec.__token:
            if ec.__token == '()':
                if ec.params is None:
                    tokens.append('()')
                else:
                    tokens.append('(' + ', '.join(
                        [param.__stringify() for param in ec.params]
                    ) + ')')
                    pass
                pass
            elif ec.__token == '[]':
                if ec.sz is not None:
                    tokens.append('[' + str(ec.sz) + ']')
                else:
                    tokens.append('[]')
                    pass
                pass
            else:
                tokens.append(ec.__token)
                pass
            ec = ec.__predecessor
            pass
        tokens.reverse()
        return ' '.join(tokens)

    # Python should translate __cast to _easycast__cast in the class.
    # This can reduce the chance of name conflict.
    def __cast(self, value):
        tp = self.__prog.type(self.__stringify())
        return drgn.cast(tp, value)

    def __call__(self, *values):
        if len(values) == 0:
            raise Exception('No value to cast')
        if len(values) == 1:
            if isinstance(values[0], self.__class__) and not values[0].__token:
                ec = self.__class__('()', self, prog=self.__prog)
                ec.params = [values[0]._]
                return ec
            if values[0] is None:
                ec = self.__class__('()', self, prog=self.__prog)
                ec.params = None
                return ec
            pass
        if len(values) > 1 or isinstance(values[0], self.__class__):
            ec = self.__class__('()', self, prog=self.__prog)
            ec.params = values
            return ec
        return self.__cast(values[0])
    pass

if __name__ == '__main__':
    class easycast_test(easycast):
        def __init__(self, token=None, predecessor=None, prog=None):
            super(easycast_test, self).__init__(token, predecessor, prog)
            pass

        # Override __cast() of easycast.
        def _easycast__cast(self, value):
            value = '(%s)%s' % (self._easycast__stringify(), value)
            return value
        pass

    _ = easycast_test()
    print(_.int(1))
    print(_.int._(1))
    print(_.int._._(1))
    print(_.int.__(1))
    print(_.struct.foo._(1))
    print(_.enum.foo._(1))
    print(_.int(_)(_.int[None], _.float.__)(1))
    print(_.int(_)(None)(1))
    print(_.int(_)[None](1))
    # Python should translate __stringify to _easycast__stringify in
    # the class.
    print(_.struct.foo._easycast__stringify)
    print(_.struct.__stringify._(1))
    print(_.struct.__cast._(1))
    pass
