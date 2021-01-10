web: waitress-serve --port=$PORT --call recommender.api:start_api
worker: python -u recommender/rq_worker.py
