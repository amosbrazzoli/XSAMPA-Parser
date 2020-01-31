import pandas as pd
import pickle
import re

class XSAMPAEntity:
    def __init__(self):
        self.xsampa = ''
        self.ipa = False
        self.description = False
        self.lenght = False
        self.stressed = False
        self.attribute = ''

    def __repr__(self):
        if self.attribute == '':
            return self.ipa
        else:
            return f'{self.ipa}-{self.attribute}'
    def is_None(self):
        if self.xsampa == '':
            return True
        else: False

    def has_attribute(self):
        if self.attribute == '':
            return True
        else: False

class XHolder(list):
    def __init__(self, *args):
        super().__init__(args)

    def __str__(self):
        out = []
        for item in args:
            if item.is_None():
                item = ' '
            elif item.has_attribute():
                # find a way to render ipa attirbtes
                pass
        return ''.join(out)

class XSAMPA:
    def __init__(self):
        df = pd.read_csv('XSAMPA-IPA.csv')
        out_dict = pd.Series(df.IPA.values, index=df.XSAMPA).to_dict()
        del(df)
        dg = pd.read_csv('Attirbutes_Table.csv')
        attr_dict = pd.Series(dg.IPA.values, index=dg.XSAMPA).to_dict()
        del(dg)
        self.dict = out_dict
        self.attr_dict = attr_dict
        self.parsed = []

    def parse(self, file):
        # Create a class feed a file handle through it and returns the parsed object
        try:
            data = file.read().split(' ')
        except:
            data = file.split(' ')
        for word in data:
            self.reco(word)



    def break_word(self, word):
        '''
        Generator Expression
        Breaks the string in patterns acccording to the XSAMPA SPECIFICATIONS
        '''
        suffixes = {"\\", "`","<"}
        char_pass = {"_"}
        prefixes = {'"','_'}
        temp = ''
        out = False
        for char in word:
            #print(char, temp, out)
            if char in suffixes:
                # Suffixes append content and prepare for yield
                out = True
            elif char in char_pass:
                # Pass characters append but do not prepare
                out = False
            elif char in prefixes:
                # Prefixes yield, append and do not prepare
                yield temp
                temp = ''
                out = False
            else:
                # Ordinary characters yield if prepared, append and prepare
                if out:
                    yield temp
                    temp = ''
                    out = False
                out = True
            temp += char
        # yields the remaining in the temp string
        yield temp

    def token_reco(self, token):
        '''
        How it shoul be done:
        1. Recognoise prefix and suffix
        2. Makes object
        3. Object rendes utf-8 IPA representation

        '''
        par_token = XSAMPAEntity()
        if len(token) == 0:
            return None
        elif len(token) == 1:
            pass
        else:
            if token[0] == '"':
                par_token.stressed = 1
                token = token[1:]
            elif token[0] == "%":
                par_token.stressed = 2
                token = token[1:]
            elif token[-2] == "_":
                par_token.attribute = self.attr_dict[token[-2:]]
                token = token[:-2]

        par_token.xsampa = token
        par_token.ipa = self.dict[token]
        return par_token

    def reco(self, word):
        for token in self.break_word(word):
            self.parsed.append(self.token_reco(token))
