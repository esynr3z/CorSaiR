#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File writers.
"""

import os
import json
import yaml
import jinja2
from corsair import __version__
from . import utils
from pathlib import Path
import wavedrom


class _DictWriter():
    """Base class that converts dictionary to file."""
    def _save_file(self, path, data):
        """Create file from dictionary."""
        with open(path, 'w') as f:
            print("  Save data to file ... ", end='')
            ext = utils.get_file_ext(path)
            if ext in ['.yaml', '.yml']:
                yaml.Dumper.ignore_aliases = lambda *args: True  # hack to disable aliases
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            elif ext == '.json':
                json.dump(data, f, indent=4)
            else:
                raise ValueError("Unknown extension '%s' of the file '%s'" % (ext, path))
            print("OK")
        return data


class RegisterMapWriter(_DictWriter):
    """Write register map to a file.

    Examples:

        Create JSON file based on a :class:`RegisterMap` object:

        >>> from corsair import RegisterMapWriter, RegisterMap
        >>> writer = RegisterMapWriter()
        >>> rmap = RegisterMap()
        >>> writer('/tmp/map.json', rmap)
        Write '/tmp/map.json' file with RegisterMapWriter:
          Prepare data ... OK
          Save data to file ... OK
    """
    def __call__(self, path, rmap):
        """Write output file.

        Args:
            path : path to file
            rmap : :class:`RegisterMap` object
        """
        print("Write '%s' file with RegisterMapWriter:" % path)
        print("  Prepare data ... ", end='')
        rmap._validate()
        data = {
            'config': rmap.config.as_dict(),
            'regmap': list(rmap.as_dict().values())
        }
        print("OK")
        self._save_file(path, data)


class ConfigurationWriter(_DictWriter):
    """Write configuration to a file.

    Examples:

        Create JSON file based on a :class:`Configuration` object:

        >>> from corsair import Configuration, ConfigurationWriter
        >>> writer = ConfigurationWriter()
        >>> config = Configuration()
        >>> writer('/tmp/config.json', config)
        Write '/tmp/config.json' file with ConfigurationWriter:
          Prepare data ... OK
          Save data to file ... OK
    """
    def __call__(self, path, config):
        """Write output file.

        Args:
            path : path to file
            rmap : :class:`Configuration` object
        """
        print("Write '%s' file with ConfigurationWriter:" % path)
        print("  Prepare data ... ", end='')
        data = config.as_dict()
        print("OK")
        self._save_file(path, data)


class _Jinja2Writer():
    """Basic class for rendering Jinja2 templates."""

    def _render_to_file(self, template, vars, path):
        """Render text with Jinja2 and save it to file

        Args:
            template : path to Jinja2 template
            vars : dictionary with template variables
            path : path to output file
        """
        print("  Load template ... ", end='')
        templates_path = str(Path(__file__).parent / 'templates')
        j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=templates_path),
                                    trim_blocks=True, lstrip_blocks=True)
        j2_template = j2_env.get_template(template)
        print("OK")

        print("  Render text ... ", end='')
        rendered_text = j2_template.render(vars)
        print("OK")

        print("  Save data to file ... ", end='')
        with open(path, "w") as f:
            f.write(rendered_text)
        print("OK")


class LbBridgeWriter(_Jinja2Writer):
    """Create HDL file with bridge to Local Bus.

    Examples:

        Create Verilog file with APB to Local Bus bridge:

        >>> from corsair import Configuration, LbBridgeWriter
        >>> config = Configuration()
        >>> config['lb_bridge']['type'].value = 'apb'
        >>> writer = LbBridgeWriter()
        >>> writer('/tmp/lb_bridge.v', config)
        Write '/tmp/lb_bridge.v' file with LbBridgeWriter:
          Prepare data ... OK
          Load template ... OK
          Render text ... OK
          Save data to file ... OK
    """
    def __call__(self, path, config):
        """Create bridge to Local Bus in Verilog."""

        if config['lb_bridge']['type'].value == 'axil':
            j2_template = 'axil2lb_verilog.j2'
        elif config['lb_bridge']['type'].value == 'apb':
            j2_template = 'apb2lb_verilog.j2'
        elif config['lb_bridge']['type'].value == 'amm':
            j2_template = 'amm2lb_verilog.j2'
        else:
            print("Local Bus is selected for the CSR interface. Bridge will not be generated.")
            return

        print("Write '%s' file with LbBridgeWriter:" % path)
        print("  Prepare data ... ", end='')

        j2_vars = {}

        j2_vars['corsair_ver'] = __version__
        j2_vars['module_name'] = Path(path).stem
        j2_vars['config'] = config

        print("OK")

        self._render_to_file(j2_template, j2_vars, path)


class HdlWriter(_Jinja2Writer):
    """Create HDL file with register map.

    Examples:
        >>> from corsair import RegisterMap, HdlWriter
        >>> rmap = RegisterMap()
        >>> writer = HdlWriter()
        >>> writer('/tmp/regs.v', rmap)
        Write '/tmp/regs.v' file with HdlWriter:
          Prepare data ... OK
          Load template ... OK
          Render text ... OK
          Save data to file ... OK
    """
    def __call__(self, path, rmap):
        """Create register map in Verilog."""
        j2_template = 'regmap_verilog.j2'

        print("Write '%s' file with HdlWriter:" % path)
        print("  Prepare data ... ", end='')
        rmap._validate()

        j2_vars = {}

        j2_vars['corsair_ver'] = __version__
        if not rmap.config['name'].value:
            rmap.config['name'].value = Path(path).stem
        j2_vars['rmap'] = rmap
        j2_vars['config'] = rmap.config

        print("OK")

        self._render_to_file(j2_template, j2_vars, path)


class DocsWriter(_Jinja2Writer):
    """Create documentation for a register map.

    Examples:
        >>> from corsair import RegisterMap, DocsWriter
        >>> rmap = RegisterMap()
        >>> writer = DocsWriter()
        >>> writer('/tmp/regs.md', rmap)
        Write '/tmp/regs.md' file with DocsWriter:
          Prepare data ... OK
          Load template ... OK
          Render text ... OK
          Save data to file ... OK
          Draw images ... OK
    """
    def __call__(self, path, rmap):
        """Create documentation for a register map in Markdown."""
        if rmap.config['docs']['type'].value == 'md':
            j2_template = 'regmap_md.j2'
        elif rmap.config['docs']['type'].value == 'asciidoc':
            j2_template = 'regmap_asciidoc.j2'
        elif rmap.config['docs']['type'].value == 'asciidoc_rus':
            j2_template = 'regmap_asciidoc_rus.j2'

        print("Write '%s' file with DocsWriter:" % path)
        print("  Prepare data ... ", end='')
        rmap._validate()

        j2_vars = {}

        j2_vars['corsair_ver'] = __version__
        if not rmap.config['name'].value:
            rmap.config['name'].value = Path(path).stem
        j2_vars['rmap'] = rmap
        j2_vars['config'] = rmap.config

        print("OK")

        self._render_to_file(j2_template, j2_vars, path)

        print("  Draw images ... ", end='')
        self._draw_regs(Path(path).parent, rmap)
        print("OK")

    def _draw_regs(self, outdir, rmap):
        imgdir = outdir / ('%s_img' % rmap.config['name'].value)
        imgdir.mkdir(exist_ok=True)

        bits = rmap.config['data_width'].value
        lanes = bits // 16 if bits > 16 else 1
        for reg in rmap:
            reg_wd = {"reg": [],
                      "options": {"bits": bits, "lanes": lanes}}
            bit_pos = -1
            for bf in reg:
                if bit_pos == -1 and bf.lsb > 0:
                    reg_wd["reg"].append({"bits": bf.lsb})
                elif bf.lsb - bit_pos > 1:
                    reg_wd["reg"].append({"bits": bf.lsb - bit_pos - 1})
                reg_wd["reg"].append({"name": bf.name, "attr": bf.access, "bits": bf.width})
                bit_pos = bf.msb
            if (bits - 1) > bit_pos:
                reg_wd["reg"].append({"bits": bits - bit_pos - 1})
            wavedrom.render(json.dumps(reg_wd)).saveas(str(imgdir / ("%s.svg" % reg.name.lower())))
