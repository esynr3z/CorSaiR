#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Run Corsair from command line with arguments.
"""

import sys
import os
import argparse
from pathlib import Path
import corsair
from . import utils

__all__ = ['main']


class ArgumentParser(argparse.ArgumentParser):
    """Inherit ArgumentParser to override the behaviour of error method."""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, '\n%s: error: %s\n' % (self.prog, message))


def parse_arguments():
    """Parse and validate arguments."""

    parser = ArgumentParser(prog=corsair.__title__,
                            description=corsair.__description__)
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s v' + corsair.__version__)
    parser.add_argument('-r', '--regmap',
                        metavar='<file>',
                        dest='regmap',
                        help='read register map from input <file>')
    parser.add_argument('-c', '--config',
                        metavar='<file>',
                        dest='config',
                        help='read configuration from <file>')
    parser.add_argument('--template-regmap',
                        metavar='<file>',
                        dest='template_regmap',
                        help='create register map template <file>')
    parser.add_argument('--template-config',
                        metavar='<file>',
                        dest='template_config',
                        help='create configuration template <file>')
    parser.add_argument('--dump-regmap',
                        metavar='<file>',
                        dest='dump_regmap',
                        help='dump register map to <file>')
    parser.add_argument('--dump-config',
                        metavar='<file>',
                        dest='dump_config',
                        help='dump configuration to <file>')
    parser.add_argument('--output-dir',
                        metavar='<dir>',
                        dest='outdir',
                        help='save all generated artifacts to <dir>')
    parser.add_argument('--hdl',
                        dest='hdl',
                        action='store_true',
                        help='generate HDL module with register map')
    parser.add_argument('--lb-bridge',
                        dest='lb_bridge',
                        action='store_true',
                        help='generate HDL module with bridge to LocalBus')
    parser.add_argument('--docs',
                        dest='docs',
                        action='store_true',
                        help='generate docs for register map')

    # check if no arguments provided
    if len(sys.argv) == 1:
        parser.parse_args(['--help'])
        # argparse will raise SystemExit here

    # get arguments namespace
    args = parser.parse_args()

    # check conflicts
    if not args.regmap and (args.hdl or args.docs):
        parser.error("Not able to proceed without -r/--regmap argument!")

    if args.lb_bridge and not (args.regmap or args.config):
        parser.error("Not able to proceed without -r/--regmap or -c/--config argument!")

    if not args.regmap and args.dump_regmap:
        parser.error("Not able to proceed without -r/--regmap argument!")

    if args.dump_config and not (args.regmap or args.config):
        parser.error("Not able to proceed without -r/--regmap or -c/--config argument!")

    return args


def main():
    """Program main."""
    # parse arguments
    args = parse_arguments()

    # create templates
    if args.template_regmap:
        regs = [corsair.Register('spam', 'Register spam', 0),
                corsair.Register('eggs', 'Register eggs', 4)]
        regs[0].add_bfields([
            corsair.BitField('foo', 'Bit field foo', lsb=0, width=7, access='rw', initial=42),
            corsair.BitField('bar', 'Bit field bar', lsb=24, width=1, access='wo', modifiers=['sc'])
        ])
        regs[1].add_bfields(corsair.BitField('baz', 'Bit field baz', lsb=16, width=16, access='ro'))
        rmap = corsair.RegisterMap()
        rmap.add_regs(regs)
        corsair.RegisterMapWriter()(args.template_regmap, rmap)

    if args.template_config:
        config = corsair.Configuration()
        corsair.ConfigurationWriter()(args.template_config, config)

    # parse input files
    if args.config:
        config = corsair.ConfigurationReader()(args.config)
    else:
        config = corsair.Configuration()

    if args.regmap:
        rmap = corsair.RegisterMapReader()(args.regmap, config)
    else:
        rmap = corsair.RegisterMap(config)

    # dump files
    if args.dump_regmap:
        corsair.RegisterMapWriter()(args.dump_regmap, rmap)

    if args.dump_config:
        corsair.ConfigurationWriter()(args.dump_config, rmap.config)

    # prepare for artifacts generation
    if args.regmap or args.config:
        # output directory
        if args.outdir:
            outdir = Path(args.outdir)
            outdir.mkdir(parents=True, exist_ok=True)
        elif args.regmap:
            outdir = Path(args.regmap).parent
        elif args.config:
            outdir = Path(args.config).parent
        # output file base name
        if config['name'].value:
            outname = config['name'].value
        elif args.regmap:
            outname = Path(args.regmap).stem
            config['name'].value = outname
        elif args.config:
            outname = Path(args.config).stem
            config['name'].value = outname

    # create register map HDL
    if args.hdl:
        hdl_name = '%s.v' % outname
        hdl_path = str(outdir / hdl_name)
        corsair.HdlWriter()(hdl_path, rmap)

    # create bridge to LocalBus HDL
    if args.lb_bridge:
        if config['lb_bridge']['type'].value == 'none':
            print("Local Bus bridge type is 'none' - no need to generate any file.")
        else:
            lb_bridge_name = '%s2lb_%s.v' % (config['lb_bridge']['type'].value, outname)
            lb_bridge_path = str(outdir / lb_bridge_name)
            corsair.LbBridgeWriter()(lb_bridge_path, config)

    # create docs
    if args.docs:
        if config['docs']['type'].value == 'md':
            doc_name = '%s.md' % outname
        elif config['docs']['type'].value == 'asciidoc':
            doc_name = '%s.asciidoc' % outname
        elif config['docs']['type'].value == 'asciidoc_rus':
            doc_name = '%s_rus.asciidoc' % outname
        doc_path = str(outdir / doc_name)
        corsair.DocsWriter()(doc_path, rmap)

    sys.exit(0)


if __name__ == '__main__':
    main()
