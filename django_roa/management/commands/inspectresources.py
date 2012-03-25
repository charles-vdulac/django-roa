from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Introspects the models and outputs a representation of resources."

    requires_model_validation = False

    def handle_noargs(self, **options):
        from django.db.models import get_models
        for model in get_models():
            if hasattr(model.objects, 'is_roa_manager'):
                print '%s (%s)' % (model.__name__, model.get_resource_url_list())
                for field in model._meta.fields:
                    print '  %s (%s)' % (field.attname, field.__class__.__name__)