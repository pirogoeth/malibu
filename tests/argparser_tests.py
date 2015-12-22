# -*- coding: utf-8 -*-
import contextlib, malibu, os, unittest
from malibu.util.args import ArgumentParser
from nose.tools import *


class ProxyObject(object):

    def __init__(self, ap):

        self.__ap = ap

    def get_ap(self):

        return self.__ap


class ArgumentParserTestCase(unittest.TestCase):

    def argumentParserSingle_test(self):

        args = ['-c']

        ap = ArgumentParser(args, mapping = {'c' : 'create'})
        ap.parse()

        self.assertEquals(ap.options['create'], True)

    def argumentParserParameterized_test(self):

        args = ['-c', 'filename.txt']

        ap = ArgumentParser(args, mapping = {'c' : 'create'})
        ap.add_option_type('c', opt = ArgumentParser.OPTION_PARAMETERIZED)
        ap.parse()

        self.assertEquals(ap.options['create'], 'filename.txt')

    def argumentParserMultiple_test(self):

        args = ['-c', 'filename.txt', '--syntax', 'plain', '-w']

        ap = ArgumentParser(args)
        ap.add_option_mapping('c', 'create')
        ap.add_option_type('c', opt = ArgumentParser.OPTION_PARAMETERIZED)

        ap.add_option_type('syntax', opt = ArgumentParser.OPTION_PARAMETERIZED)

        ap.add_option_mapping('w', 'watch')
        ap.parse()

        self.assertEquals(ap.options['create'], 'filename.txt')
        self.assertEquals(ap.options['syntax'], 'plain')
        self.assertEquals(ap.options['watch'], True)

    def argumentParserDashedParms_test(self):

        args = ['--target', '-19000000', '--message', 'Test']

        ap = ArgumentParser(args)
        ap.add_option_type('target', opt = ArgumentParser.OPTION_PARAMETERIZED)
        ap.add_option_type('message', opt = ArgumentParser.OPTION_PARAMETERIZED)

        ap.parse()

        self.assertEquals(ap.options['target'], '-19000000')
        self.assertEquals(ap.options['message'], 'Test')

    def argumentParserQuotedDashedParms_test(self):

        args = ['--target', '"-19000000"', '--message', 'Test']

        ap = ArgumentParser(args)
        ap.add_option_type('target', opt = ArgumentParser.OPTION_PARAMETERIZED)
        ap.add_option_type('message', opt = ArgumentParser.OPTION_PARAMETERIZED)

        ap.parse()

        self.assertEquals(ap.options['target'], '-19000000')
        self.assertEquals(ap.options['message'], 'Test')

    def argumentParserQuotedParms_test(self):

        args = ['--target', '"-19000000"', '--message', "'Test'",
                '--file', '"unmatched.txt']

        ap = ArgumentParser(args)
        ap.add_option_type('target', opt = ArgumentParser.OPTION_PARAMETERIZED)
        ap.add_option_type('message', opt = ArgumentParser.OPTION_PARAMETERIZED)
        ap.add_option_type('file', opt = ArgumentParser.OPTION_PARAMETERIZED)

        ap.parse()

        self.assertEquals(ap.options['target'], '-19000000')
        self.assertEquals(ap.options['message'], 'Test')
        self.assertEquals(ap.options['file'], 'unmatched.txt')

    def argumentParserContextMgr_test(self):

        args = ['-c', 'filename.txt', '--syntax', 'plain', '-w']

        ap = ArgumentParser(args)
        pr = ProxyObject(ap)

        with pr.get_ap() as cap:
            cap.add_option_mapping('c', 'create')
            cap.add_option_type('create', opt = ArgumentParser.OPTION_PARAMETERIZED)
            cap.add_option_type('c', opt = ArgumentParser.OPTION_PARAMETERIZED)

            cap.add_option_type('syntax', opt = ArgumentParser.OPTION_PARAMETERIZED)

            cap.add_option_mapping('w', 'watch')

        ap.parse()

        self.assertEquals(ap.options['create'], 'filename.txt')
        self.assertEquals(ap.options['syntax'], 'plain')
        self.assertEquals(ap.options['watch'], True)
