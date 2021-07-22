from dotenv import dotenv_values

PARAMETERS = dotenv_values("parameters.env")
PARAMETERS.update({
    "DELAY": int(PARAMETERS['DELAY']) if 'DELAY' in PARAMETERS else 10,
    "BAUDRATE": int(PARAMETERS['BAUDRATE']) if 'BAUDRATE' in PARAMETERS else 9600,
    "IGNORE_PORTS": PARAMETERS['IGNORE_PORTS'].split(',') if 'IGNORE_PORTS' in PARAMETERS else []
})

for parameter, value in PARAMETERS.items():
    globals()[parameter] = value


__all__ = ['PARAMETERS'] + list(PARAMETERS)
