from registration.backends import get_backend


def stats(request):
    backend = get_backend('default')
    profiles = backend.get_unmoderated_profiles(request)
    return {'unmoderated_accounts': profiles.count()}
