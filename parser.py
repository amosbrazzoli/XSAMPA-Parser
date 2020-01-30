import pandas as pd
import pickle
import re

with open("/home/amosbrazzoli/Downloads/X-SAMPA-Wikipedia.html",  'r', encoding="utf-8") as xsampa_page:
    content = xsampa_page.read()
    row = r'''<td><code>(.*)</code></td>\n<td><span title=".*" class="IPA">(.*)</span></td>\n<td><a\b.*/></a></td>\n<td><a href=".*".*title="([\w&\s]*)">.*</a></td>'''
    pattern = re.compile(row)
    matches = pattern.finditer(content)
    out = []
    for match in matches:
        out.append(match.group(1,2,3))

df = pd.DataFrame.from_records(out, columns=["XSAMPA","IPA","Desc"])
df["Length"] = df.XSAMPA.apply(len)

xsampa = df.XSAMPA.to_list()
ipa = df.IPA.to_list()
lenght = df.Length.to_list()

out_dict = {}
# Structured as { lenght : {xsampa : ipa, ...}, ...}
for x, i, l in zip(xsampa, ipa, lenght):
    out_dict.setdefault(l,{}).update({x: i})

class XSAMPAEntity:
    def __init__(self):
        self.xsampa = ''
        self.ipa = False
        self.description = False
        self.lenght = False
        self.stressed = False
        self.modifiers = False

    def __repr__(self):
        return self.ipa

class XSAMPA:
    def __init__(self):
        self.dict = out_dict
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
                par_token.attribute = token[-2:]
                token = token[:-2]

        par_token.xsampa = token
        par_token.ipa = self.dict[len(token)][token]
        return par_token

    def reco(self, word):
        for token in self.break_word(word):
            self.parsed.append(self.token_reco(token))


in_string = '''ai m_< "im@s'''
parser = XSAMPA()
parser.parse(in_string)
print(parser.parsed)
