# streamlit_and_api_load_testing
Locust-Selenium for load testing a webapp and API simultanously



# RUN

<!-- locust -f src/locustfile.py --headless -u 2 -r 2 --run-time 1m --html report.html -->
locust -f src/locustfile.py --headless -u 2 -r 1 --run-time 20s --html data/report.html --host=https://www.cloud-quests.link --csv data/report.csv --csv-full-history

