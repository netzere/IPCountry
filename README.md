## Forter Home Assignment

### Implementation
- Python3 (Flask)
- Mongo (stores all requests, for rate liming and percentile metrics)
- Redis (IP Class B cache)

#### How To Run
1. Change the API access keys in the `docker-compose.yml`
2. `docker-compose up`

Alternatively, you can setup redis and mongo on your local machine, install the dependencies and run `flask run`

#### Tests
Didn't have the time to add proper testing, but provided a basic tests file to see the API in action.  
To run it: `python3 tests/tests.py`  

My tests only run 5 request against the API, because i set in the `docker-compose.yml` the rate limit of each vendor to be 2  
If If play with the rate limit and the testing, please change it accordigly.

#### Configuration
To change the rate limit for each vendor, you can modify the relevant env var in the `docker-compose.yml` file

#### Caveats
- Decent error handling is missing (around the db, cache and the IPGeo vendors APIs)
- I didn't invest time in error handling if the keys are incorrect
- The rate limiting is naive and based on the client ip to determine a unique user.

