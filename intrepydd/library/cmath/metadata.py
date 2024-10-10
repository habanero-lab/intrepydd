from mytypes import float64

m = 'cmath'

funcinfo = {
    'exp': (float64, m),
    'log': 'exp',
    'pow': 'exp',
    'sqrt': 'exp',
    'cbrt': 'exp',

    # Rounding and remainder functions
    'ceil': 'exp',
    'floor': 'exp',

    # TODO: to add more
}
