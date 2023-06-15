class Pattern:
    def __init__(self, line=None):
        if line is not None:
            items, supp = line.split(' #SUP: ')
            self.items = set(map(int, items.split(' ')))
            self.supp = int(supp)
        else:
            self.items = set()
            self.supp = 0

        self.transactions = set()
        self.pearson = 0.0
        self.intercept = 0.0
        self.slope = 0.0
        self.pvalue = 0.0
        self.items_word = set()

    def to_dict(self):
        return {'p': list(self.items_word),
                'len_p': len(self.items),
                't': list(self.transactions),
                'len_t': self.supp,
                'pe': self.pearson,
                'const': self.intercept,
                'alfa': self.slope,
                'pvalue': self.pvalue
                }

    @classmethod
    def from_dict(cls, pattern):
        p = Pattern()
        p.items = set(pattern['items'])
        p.supp = pattern['supp']
        p.transactions = pattern['transactions']
        p.slope = pattern['slope']
        return p

    def __repr__(self):
        return f"{' '.join(map(str, self.items))}; supp: {self.supp}; " \
               f"in: {','.join(map(str, self.transactions))}"
