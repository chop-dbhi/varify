from avocado.formatters import registry as formatters
from serrano.formatters import HTMLFormatter


class FowardSlashDelimited(HTMLFormatter):
    delimiter = ' / '


class CommaSeparated(HTMLFormatter):
    delimiter = ', '


formatters.register(HTMLFormatter, 'HTML')
formatters.register(FowardSlashDelimited, 'Forward-slash Delimited')
formatters.register(CommaSeparated, 'Comma-separated')
