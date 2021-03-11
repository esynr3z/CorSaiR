#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Configuration module.
"""

from . import utils


class Parameter():
    """Generic parameter.

    Examples:

        Create parameter with check that value never exceed 42:

        >>> print(Parameter('param_name', 42, lambda val: val <= 42))
        param_name: 42

    Attributes:
        name: Name of the parameter.
        validator: Lambda function to perform value validation.
            Returns True if value check is OK, and False otherwise.
    """
    def __init__(self, name, value=None, validator=lambda val: True):
        self._value = None

        self.name = name
        self.validator = validator
        self.value = value

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            raise TypeError("Failed to compare '%s' with '%s'!" % (repr(self), repr(other)))
        else:
            return (
                self.as_dict() == other.as_dict() and
                self.validator == other.validator
            )

    def __ne__(self, other):
        if self.__class__ != other.__class__:
            raise TypeError("Failed to compare '%s' with '%s'!" % (repr(self), repr(other)))
        else:
            return not self.__eq__(other)

    def __repr__(self):
        return 'Parameter(%s, %s)' % (repr(self.name), repr(self.value))

    def __str__(self):
        return self.as_str()

    def as_str(self, indent=''):
        """Returns indented parameter's string with name and value."""
        return indent + '%s: %s' % (self.name, utils.try_int_to_str(self._value))

    def as_dict(self):
        """Returns dictionary with parameters's name and value."""
        return {'name': self.name, 'value': self.value}

    @property
    def value(self):
        """Value of the parameter.

        Getter:
            Get current value of the parameter.

        Setter:
            Set new value of the parameter.

            Raises:
                ValueError: An error occured if new value fails the check.
        """
        return self._value

    @value.setter
    def value(self, new_value):
        # store all 0x-like hexademical strings as integers if possible
        self._value = utils.try_hex_to_dec(new_value)
        # run validator for the new value
        self._validate()

    def _validate(self):
        """Check parameter value correctness."""
        if self.validator(self.value) is False:
            raise ValueError('"%s" parameter with "%s" value failed the check!' % (self.name,
                                                                                   self.value))


class ParameterGroup():
    """Group of parameters or other groups.

    Examples:

        Create group and add parameters:

        >>> pg = ParameterGroup('group_a')
        >>> pg.add_params([Parameter('p1', 42), Parameter('p2', 'abc')])
        >>> print(pg)
        group_a:
          p1: 42
          p2: abc

        Other way to do the same:

        >>> pg = ParameterGroup('group_a')
        >>> pg.values = {'p1':42, 'p2':'abc'}
        >>> print(pg)
        group_a:
          p1: 42
          p2: abc

        Change parameter value:

        >>> pg = ParameterGroup('group_a')
        >>> pg.add_params(Parameter('p1', 42))
        >>> pg['p1'].value = 777
        >>> print(pg['p1'].value)
        777

    Attributes:
        name: Name of the group.
    """
    def __init__(self, name):
        self.name = name
        self._params = {}

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            raise TypeError("Failed to compare '%s' with '%s'!" % (repr(self), repr(other)))
        else:
            return self.as_dict() == other.as_dict()

    def __ne__(self, other):
        if self.__class__ != other.__class__:
            raise TypeError("Failed to compare '%s' with '%s'!" % (repr(self), repr(other)))
        else:
            return not self.__eq__(other)

    def __repr__(self):
        return 'ParameterGroup(%s)' % repr(self.name)

    def __str__(self):
        return self.as_str()

    def __getitem__(self, key):
        try:
            return self._params[key]
        except KeyError:
            raise KeyError("Parameter/Group with a name '%s' doesn't exist!" % key)

    def __setitem__(self, key, value):
        raise KeyError("Not able to set '%s' item directly in '%s' group!"
                       " Try use add_params() method." % (key, self.name))

    def as_str(self, indent=''):
        """Returns indented string with group members and their values"""
        new_indent = indent + '  '
        params = [self[name].as_str(new_indent) for name in self.names]
        params_str = '\n'.join(params) if params else new_indent + 'empty'
        return indent + '%s:\n' % self.name + params_str

    def as_dict(self):
        """Returns dictionary with group's key attributes."""
        return self.values

    @property
    def names(self):
        """Names of all parameters/groups contained."""
        return self._params.keys()

    @property
    def params(self):
        """List with parameters/groups objects contained."""
        return [param for param in self._params.items()]

    def add_params(self, new_params):
        """Add parameters.

        Args:
            new_params : list with parameters/groups or single object
        """
        # hack to handle single elements
        new_params = utils.listify(new_params)

        # add params to dict one by one
        for p in new_params:
            if p.name in self._params:
                raise KeyError("Item with name '%s' is already present in '%s' group!" % (p.name, self.name))
            self._params[p.name] = p

    @property
    def values(self):
        """Dictionary with values of the parameters/groups.

        Getter:
            Returns dictionary with pairs {name:value} of all parameter/groups of the current group.

        Setter:
            Sets only parameters/groups specified in the input dictionary,
            but if parameter/group does not exist, it will create it.
        """
        values = {}
        for name in self.names:
            if isinstance(self[name], ParameterGroup):
                values[name] = self[name].values
            else:
                values[name] = self[name].value
        return values

    @values.setter
    def values(self, new_values):
        for name in new_values.keys():
            try:
                # if parameter/group exists
                if isinstance(self[name], ParameterGroup):
                    self[name].values = new_values[name]
                else:
                    self[name].value = new_values[name]
            except KeyError:
                # else if parameter/group does not exists
                if isinstance(new_values[name], dict):
                    self.add_params(ParameterGroup(name=name))
                    self[name].values = new_values[name]
                else:
                    self.add_params(Parameter(name=name, value=new_values[name]))


class Configuration(ParameterGroup):
    """Collection of global parameters."""
    def __init__(self):
        super().__init__('configuration')
        self._init_default_params()

    def __repr__(self):
        return 'Configuration()'

    def _init_default_params(self):
        """Initalize all default params"""
        # group regmap
        self.add_params(ParameterGroup('regmap'))
        self['regmap'].add_params([
            Parameter(name='read_filler', value=0x0),
            Parameter(name='address_increment_mode', value='none',
                      validator=lambda val: val in ['none', 'data_width', 'custom']),
            Parameter(name='address_increment_value', value=4, validator=lambda val: val >= 1),
            Parameter(name='address_alignment_mode', value='data_width',
                      validator=lambda val: val in ['none', 'data_width', 'custom']),
            Parameter(name='address_alignment_value', value=4, validator=lambda val: val >= 1)
        ])

        # group lb_bridge
        self.add_params(ParameterGroup('lb_bridge'))
        lb_bridge_type_allowed = ['amm', 'apb', 'axil', 'none']
        self['lb_bridge'].add_params(
            Parameter(name='type', value='none', validator=lambda val: val in lb_bridge_type_allowed)
        )

        # group docs
        self.add_params(ParameterGroup('docs'))
        docs_type_allowed = ['md', 'asciidoc', 'asciidoc_rus']
        self['docs'].add_params(
            Parameter(name='type', value='md', validator=lambda val: val in docs_type_allowed)
        )

        # common params
        data_width_allowed = {
            'amm': [8, 16, 32, 64, 128, 256, 512, 1024],
            'apb': [8, 16, 32],
            'axil': [32, 64],
            'none': [8, 16, 32, 64, 128, 256, 512, 1024]
        }
        self.add_params(Parameter(
            name='data_width',
            value=32,
            validator=lambda val: val in data_width_allowed[self['lb_bridge']['type'].value])
        )

        addr_width_allowed = {
            'amm': range(1, 65),
            'apb': range(1, 33),
            'axil': [32, 64],
            'none': range(1, 65)
        }
        self.add_params(Parameter(
            name='address_width',
            value=32,
            validator=lambda val: val in addr_width_allowed[self['lb_bridge']['type'].value])
        )

        self.add_params([
            Parameter(name='name', value=''),
            Parameter(name='version', value='1.0')]
        )

        reg_rst_allowlist = ['sync_pos', 'sync_neg', 'async_pos', 'async_neg']
        self.add_params(Parameter(name='register_reset', value='sync_pos',
                                  validator=lambda val: val in reg_rst_allowlist))
