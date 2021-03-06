#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Configuration module tests.
"""

import pytest
from corsair import Parameter, ParameterGroup, Configuration
import copy


class TestParameter:
    """Class 'Parameter' testing"""
    def test_create(self):
        """Test of a parameter creation"""
        p_name = "param_a"
        p_val = 42
        p = Parameter(p_name, p_val)
        print(p)
        print(repr(p))
        assert p.name == p_name
        assert p.value == p_val

    def test_eq(self):
        """Test of equality comparision of parameters."""
        p1 = Parameter('par_a', 42)
        p2 = copy.deepcopy(p1)
        assert p1 == p2

    def test_ne(self):
        """Test of non equality comparision of parameters."""
        p1 = Parameter('par_a', 42)
        p2 = copy.deepcopy(p1)
        p2.validator = lambda val: val != 777
        assert p1 != p2

    def test_modify(self):
        """Test of a parameter creation"""
        p = Parameter("param_a", 42)
        p_new_val = 'hello'
        p.value = p_new_val
        assert p.value == p_new_val

    def test_allowlist(self):
        """Test of a parameter allowlist check"""
        with pytest.raises(ValueError):
            Parameter("param_a", 'aaa', validator=lambda val: val in ['bbb', 'ccc'])

    def test_min(self):
        """Test of a parameter min check"""
        with pytest.raises(ValueError):
            Parameter("param_a", 5, validator=lambda val: val >= 0xF)

    def test_max(self):
        """Test of a parameter max check"""
        with pytest.raises(ValueError):
            Parameter("param_a", 32, validator=lambda val: val < 32)

    def test_range_less(self):
        """Test of a parameter range check: if value is less"""
        with pytest.raises(ValueError):
            Parameter("param_a", 5, validator=lambda val: 100 <= val < 200)

    def test_range_greater(self):
        """Test of a parameter range check: if value is greater"""
        with pytest.raises(ValueError):
            Parameter("param_a", 300, validator=lambda val: 100 <= val < 200)


class TestParameterGroup:
    """Class 'ParameterGroup' testing"""
    def test_create(self):
        """Test of a parameter group creation"""
        p1_name = 'param_a'
        p1_val = 42
        p2_name = 'param_b'
        p2_val = 'value_b'
        p3_name = 'param_c'
        p3_val = True
        params = [
            Parameter(p1_name, p1_val),
            Parameter(p2_name, p2_val),
            Parameter(p3_name, p3_val)
        ]

        pg_name = 'group_a'
        pg = ParameterGroup(pg_name)
        pg.add_params(params)
        print(pg)
        assert pg.name == pg_name
        assert pg[p2_name].value == p2_val

    def test_eq(self):
        """Test of equality comparision of parameters groups."""
        pg1 = ParameterGroup('group_a')
        pg1.add_params([
            Parameter('p1', 42),
            Parameter('p2', '0x42'),
        ])
        pg2 = copy.deepcopy(pg1)
        assert pg1 == pg2

    def test_ne(self):
        """Test of non equality comparision of parameters groups."""
        pg1 = ParameterGroup('group_a')
        pg1.add_params([
            Parameter('p1', 42),
            Parameter('p2', '0x42'),
        ])
        pg2 = copy.deepcopy(pg1)
        pg2['p2'].value = 'lol'
        assert pg1 != pg2

    def test_add_single_param(self):
        """Test of adding a parameter to a group"""
        p1_name = 'param_a'
        p1_val = 42
        p1 = Parameter(p1_name, p1_val)
        pg = ParameterGroup('group_a')
        pg.add_params(p1)
        print(pg)
        assert pg[p1_name].value == p1_val

    def test_add_multiple_param(self):
        """Test of adding a parameter to a group"""
        p1_name = 'param_a'
        p1_val = 42
        p1_name = 'param_a'
        p1_val = 42
        p2_name = 'param_b'
        p2_val = 'value_b'
        p1 = Parameter(p1_name, p1_val)
        p2 = Parameter(p2_name, p2_val)
        pg = ParameterGroup('group_a')
        pg.add_params([p1, p2])
        print(pg)
        assert pg[p2_name].value == p2_val

    def test_add_twice(self):
        """Test of adding a parameter to a group twice"""
        p1_name = 'param_a'
        p1_val = 42
        p1 = Parameter(p1_name, p1_val)
        pg = ParameterGroup('group_a')
        pg.add_params(p1)
        with pytest.raises(KeyError):
            pg.add_params(p1)


class TestConfiguration:
    """Class 'Configuration' testing"""
    def test_create(self):
        """Test of a configuration creation"""
        p1_name = 'param_a'
        p1_val = 42
        p1 = Parameter(p1_name, p1_val)
        p2_name = 'param_b'
        p2_val = 'value_b'
        p2 = Parameter(p2_name, p2_val)
        pg_name = 'group_a'
        pg = ParameterGroup(pg_name)
        pg.add_params([p1, p2])
        p3_name = 'param_c'
        p3_val = True
        p3 = Parameter(p3_name, p3_val)
        config = Configuration()
        config.add_params([pg, p3])
        print(config)
        assert config[pg_name][p1_name].value == p1_val
        assert config[p3_name].value == p3_val

    def test_add_single_param(self):
        """Test of adding a parameter to the configuration"""
        p1_name = 'param_a'
        p1_val = 42
        p1 = Parameter(p1_name, p1_val)
        config = Configuration()
        config.add_params(p1)
        print(config)
        assert config[p1_name].value == p1_val

    def test_add_multiple_param(self):
        """Test of adding a parameter to a group"""
        p1_name = 'param_a'
        p1_val = 42
        p1_name = 'param_a'
        p1_val = 42
        p2_name = 'param_b'
        p2_val = 'value_b'
        p1 = Parameter(p1_name, p1_val)
        p2 = Parameter(p2_name, p2_val)
        config = Configuration()
        config.add_params([p1, p2])
        print(config)
        assert config[p2_name].value == p2_val

    def test_add_group(self):
        """Test of adding a parameter group to the configuration"""
        p1_name = 'param_a'
        p1_val = 42
        p1 = Parameter(p1_name, p1_val)
        p2_name = 'param_b'
        p2_val = 'value_b'
        p2 = Parameter(p2_name, p2_val)
        pg_name = 'group_a'
        pg = ParameterGroup(pg_name)
        pg.add_params([p1, p2])
        config = Configuration()
        config.add_params(pg)
        p3_name = 'param_c'
        p3_val = True
        p3 = Parameter(p3_name, p3_val)
        config[pg_name].add_params(p3)
        print(config)
        assert config[pg_name][p3_name].value == p3_val

    def test_set_values(self):
        """Test of loading new values to a configuration"""
        config = Configuration()
        new_values = {
            'read_filler': 42,
            'regmap': {
                'address_increment_mode': 'custom',
                'address_increment_value': 16
            },
            'parameter_a': 777,
            'group_a': {
                'par_deafbeef': 55,
                'group_b': {
                    'cafe': 'noname',
                    'address': 68,
                }
            }
        }
        config.values = new_values
        print(config)
        assert new_values['read_filler'] == config['read_filler'].value
        assert (new_values['regmap']['address_increment_mode'] ==
                config['regmap']['address_increment_mode'].value)
        assert new_values['group_a'] == config['group_a'].values

    def test_address_calculation_validator(self):
        config = Configuration()
        # no exception here
        print(config['regmap']['address_increment_mode'])
        config['regmap']['address_increment_mode'].value = 'data_width'
        print(config['regmap']['address_increment_mode'])
        # exception on not allowed value
        with pytest.raises(ValueError):
            config['regmap']['address_increment_mode'].value = 'lalala'

    def test_lb_bridge_type_validator(self):
        config = Configuration()
        # no exception here
        print(config['lb_bridge']['type'])
        print(config['data_width'])
        config['data_width'].value = 8
        print(config['data_width'])
        config['data_width'].value = 32
        print(config['data_width'])
        # change interface type
        config['lb_bridge']['type'].value = 'apb'
        print(config['lb_bridge']['type'])
        # exception on not allowed value
        with pytest.raises(ValueError):
            config['data_width'].value = 64
