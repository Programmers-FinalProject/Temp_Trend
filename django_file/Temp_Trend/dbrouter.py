class DBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'weather':
            if model._meta.model_name in ['weatherdata', 'raw_data_weatherstn', 'weatherstation']:
                return 'redshift'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'weather':
            if model._meta.model_name in ['weatherdata', 'raw_data_weatherstn', 'weatherstation']:
                return 'redshift'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'weather' and obj2._meta.app_label == 'weather':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'weather':
            if model_name in ['weatherdata', 'raw_data_weatherstn', 'weatherstation']:
                return db == 'redshift'
        return db == 'default'
