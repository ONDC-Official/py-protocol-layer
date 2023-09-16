from flask_restx import Namespace, Resource

from main.cron.search_by_city import make_full_catalog_search_requests, make_incremental_catalog_search_requests

cron_namespace = Namespace('cron', description='Cron Job Namespace')


@cron_namespace.route("/cron/search/full-catalog")
class FullCatalogSearch(Resource):

    def post(self):
        make_full_catalog_search_requests()
        return {"status": "success"}, 200


@cron_namespace.route("/cron/search/incremental-start")
class IncrementalCatalogSearch(Resource):

    def post(self):
        make_incremental_catalog_search_requests(mode="start")
        return {"status": "success"}, 200


@cron_namespace.route("/cron/search/incremental-stop")
class IncrementalCatalogSearch(Resource):

    def post(self):
        make_incremental_catalog_search_requests(mode="stop")
        return {"status": "success"}, 200

