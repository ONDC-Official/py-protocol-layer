import os
from flask_restx import Api as BaseAPI

from routes.callback import callback_namespace
from routes.request import request_namespace
from routes.request_dump import request_dump_namespace


class Api(BaseAPI):
    def _register_doc(self, app_or_blueprint):
        # HINT: This is just a copy of the original implementation with the last line commented out.
        if self._add_specs and self._doc:
            # Register documentation before root if enabled
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
        # app_or_blueprint.add_url_rule(self._doc, 'root', self.render_root)

    @property
    def base_path(self):
        return ''


api = Api(
    title='ONDC API',
    version='1.0',
    description='Rest api for ONDC dashboard project',
    doc='/swagger/' if os.getenv("ENV") != None else False
)


api.add_namespace(callback_namespace, path='/protocol')
api.add_namespace(request_namespace, path='/protocol')
api.add_namespace(request_dump_namespace, path='/protocol')
# api.add_namespace(cron_namespace, path='/protocol')
# api.add_namespace(ondc_network_test_namespace, path='/protocol/test')
# api.add_namespace(logs_namespace, path='/protocol')
