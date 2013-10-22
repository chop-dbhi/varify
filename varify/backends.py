import ldap

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        # username is really the email address...
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return


class LdapBackend(ModelBackend):
    """Authenticate a user against LDAP.

    Requires python-ldap to be installed.

    Requires the following things to be in settings.py:

        DEBUG - boolean
            Uses logging module for debugging messages.

        SERVER_URI -- string, ldap uri.
            default: 'ldap://localhost'

        SEARCHDN -- string of the LDAP dn to use for searching
            default: 'dc=localhost'

        SCOPE -- one of: ldap.SCOPE_*, used for searching
            see python-ldap docs for the search function
            default = ldap.SCOPE_SUBTREE

        SEARCH_FILTER -- formated string, the filter to use for searching for a
            user. Used as: filterstr = SEARCH_FILTER % username
            default = 'cn=%s'

        UPDATE_FIELDS -- boolean, do we sync the db with ldap on each auth
            default = True

    Required unless FULL_NAME is set:

        FIRST_NAME -- string, LDAP attribute to get the given name from
        LAST_NAME -- string, LDAP attribute to get the last name from

    Optional Settings:

        FULL_NAME -- string, LDAP attribute to get name from, splits on ' '
        GID -- string, LDAP attribute to get group name/number from
        SU_GIDS -- list of strings, group names/numbers that are superusers
        STAFF_GIDS -- list of strings, group names/numbers that are staff
        EMAIL -- string, LDAP attribute to get email from
        DEFAULT_EMAIL_SUFFIX -- string, appened to username if no email found
        OPTIONS -- hash, python-ldap global options and their values
            {ldap.OPT_X_TLS_CACERTDIR: '/etc/ldap/ca/'}
        ACTIVE_FIELD -- list of strings, LDAP attribute to get active status
            from
        ACTIVE -- list of strings, allowed for active from ACTIVE_FIELD

    You must pick a method for determining the DN of a user and set the needed
    settings:
        - You can set BINDDN and BIND_ATTRIBUTE like:
            BINDDN = 'ou=people,dc=example,dc=com'
            BIND_ATTRIBUTE = 'uid'
          and the user DN would be:
            'uid=%s,ou=people,dc=example,dc=com' % username

        - Look for the DN on the directory, this is what will happen if you do
          not define the BINDDN setting. In that case you may need to
          define PREBINDDN and PREBINDPW if your LDAP server does not
          allow anonymous queries. The search will be performed with the
          SEARCH_FILTER setting.

        - Override the _pre_bind() method, which receives the ldap object and
          the username as it's parameters and should return the DN of the user.
    """

    settings = {
              'SERVER_URI': 'ldap://localhost',
              'SEARCHDN': 'dc=localhost',
              'SCOPE': ldap.SCOPE_SUBTREE,
              'SEARCH_FILTER': 'cn=%s',
              'UPDATE_FIELDS': True,
              'PREBINDDN': None,
              'PREBINDPW': None,
              'BINDDN': None,
              'BIND_ATTRIBUTE': None,
              'OPTIONS': None,
              'DEBUG': True,
      }

    def __init__(self):
        ldap_settings = getattr(settings, 'LDAP', {})
        self.settings.update(ldap_settings)

    # Functions provided to override to customize to your LDAP configuration.
    def _pre_bind(self, conn, username):
        "Function that returns the dn to bind against LDAP with"
        if not self.settings['BINDDN']:
            # When the BINDDN setting is blank we try to find the
            # dn binding anonymously or using PREBINDDN
            if self.settings['PREBINDDN']:
                try:
                    conn.simple_bind_s(self.settings['PREBINDDN'],
                            self.settings['PREBINDPW'])
                except ldap.LDAPError, exc:
                    return

            # Now do the actual search
            filter = self.settings['SEARCH_FILTER'] % username
            result = conn.search_s(self.settings['SEARCHDN'],
                        self.settings['SCOPE'], filter, attrsonly=1)

            if len(result) != 1:
                return
            return result[0][0]
        else:
            # BINDDN is set so we use it as a template.
            return "%s=%s,%s" % (self.settings['BIND_ATTRIBUTE'], username,
                    self.settings['BINDDN'])

    def authenticate(self, username=None, password=None):
        # handle an email address being supplied
        idx = username.find('@')
        if idx > -1:
            email = username
            username = username[:idx]

        # test up front if an account for this user exists before testing it
        # against the LDAP connection
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return

        if self.settings['OPTIONS']:
            for k in self.settings['OPTIONS']:
                ldap.set_option(k, self.settings.OPTIONS[k])

        # initialize connection to the server
        conn = ldap.initialize(self.settings['SERVER_URI'])
        bind_string = self._pre_bind(conn, username)

        if not bind_string:
            return

        try:
            # Try to bind as the provided user. We leave the bind until
            # the end for other ldap.search_s call to work authenticated.
            conn.bind_s(bind_string, password)
        except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM), e:
            return
        finally:
            conn.unbind_s()

        return user
