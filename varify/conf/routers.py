class NoSyncDbRouter(object):
    using = None
    schema = None
    app_labels = []

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.app_labels:
            return self.using

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.app_labels:
            return self.using

    def schema_for_db(self, model, database, **hints):
        if model._meta.app_label in self.app_labels:
            return self.schema

    def allow_syncdb(self, db, model):
        pass


class VariantsRouter(NoSyncDbRouter):
    schema = 'variants'
    app_labels = ['variants']


class SamplesRouter(NoSyncDbRouter):
    schema = 'samples'
    app_labels = ['samples']


class DiseasesRouter(NoSyncDbRouter):
    schema = 'diseases'
    app_labels = ['diseases']


class GenesRouter(NoSyncDbRouter):
    schema = 'genes'
    app_labels = ['genes']


class LiteratureRouter(NoSyncDbRouter):
    schema = 'literature'
    app_labels = ['literature']


class SourcesRouter(NoSyncDbRouter):
    schema = 'sources'
    app_labels = ['sources']


class GenomeRouter(NoSyncDbRouter):
    schema = 'genome'
    app_labels = ['genome']
