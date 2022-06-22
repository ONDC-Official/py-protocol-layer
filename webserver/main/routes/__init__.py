import os

from flask import g, request
from flask_restx import Api as BaseAPI
from jsonschema import ValidationError
from werkzeug.exceptions import BadRequest

from main.routes.cancel import cancel_namespace
from main.routes.cancellation_reasons import cancellation_reasons_namespace
from main.routes.confirm import confirm_namespace
from main.routes.init import init_namespace
from main.routes.rating import rating_namespace
from main.routes.search import search_namespace
from main.routes.select import select_namespace
from main.routes.status import status_namespace
from main.routes.support import support_namespace
from main.routes.track import track_namespace
from main.utils.original_schema_utils import validate_data_with_original_schema


class Api(BaseAPI):
    def _register_doc(self, app_or_blueprint):
        # HINT: This is just a copy of the original implementation with the last line commented out.
        if self._add_specs and self._doc:
            # Register documentation before root if enabled
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
        #app_or_blueprint.add_url_rule(self._doc, 'root', self.render_root)

    @property
    def base_path(self):
        return ''


api = Api(
    title='ONDC API',
    version='1.0',
    description='Rest api for ONDC dashboard project',
    doc='/swagger/' if os.getenv("ENV") != None else False
)

# api.render_root()


@api.errorhandler(BadRequest)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        validate_data_with_original_schema(request.get_json(), '/on_search', passing_in_python_protocol=False)
        original_error = error.description
        return {'error': str(original_error), 'message': original_error.message}, 400
    # handle other "Bad Request"-errors
    return str(error), 400


@api.errorhandler(ValidationError)
def bad_request(error):
    return {'error': str(error), 'message': error.message}, 400


api.add_namespace(cancel_namespace, path='/protocol')
api.add_namespace(cancellation_reasons_namespace, path='/protocol')
api.add_namespace(confirm_namespace, path='/protocol')
api.add_namespace(init_namespace, path='/protocol')
api.add_namespace(rating_namespace, path='/protocol')
api.add_namespace(search_namespace, path='/protocol')
api.add_namespace(select_namespace, path='/protocol')
api.add_namespace(status_namespace, path='/protocol')
api.add_namespace(support_namespace, path='/protocol')
api.add_namespace(track_namespace, path='/protocol')
