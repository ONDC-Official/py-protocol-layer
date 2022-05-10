import os

from flask_restx import Api as BaseAPI
from jsonschema import ValidationError
from werkzeug.exceptions import BadRequest

from main.routes.search import search_namespace


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
        original_error = error.description
        return {'error': str(original_error), 'message': original_error.message}, 400
    # handle other "Bad Request"-errors
    return str(error), 400


@api.errorhandler(ValidationError)
def bad_request(error):
    return {'error': str(error), 'message': error.message}, 400


api.add_namespace(search_namespace, path='/protocol')
