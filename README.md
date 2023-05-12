dionysus
===

![build-docker-image workflow](https://github.com/wsg-ariadne/dionysus/actions/workflows/build-docker-image.yml/badge.svg)

📚 Dionysus is the backend for the Ariadne project. It is made up of three parts:

1. An instance of the [Calliope](https://github.com/wsg-ariadne/calliope) model, which classifies cookie banner text as 'good' (i.e., clear enough, likely not deceptive) or 'bad' (i.e., intent is not clear, likely deceptive).
2. An instance of the [Janus](https://github.com/wsg-ariadne/janus) model, which classifies options or checkboxes in a cookie banner screencapture as 'absent' (no options detected), 'even' (evenly-weighted options detected), or 'weighted' (unevenly-weighted options detected).
3. A connection to a PostgreSQL database that stores user-generated reports of deceptive design in webpages, along with a [REST API](#api) that allows for report management and model usage.

## Installation

You will need Python 3.8+ (tested on 3.8.16). It is recommended to use a virtual environment.

```bash
python3 -m .venv venv
source .venv/bin/activate
```

Dionysus uses SQLAlchemy to interface with the Postgres database, so you will need to install the appropriate driver for your system. On Debian-based systems, this is `libpq-dev`:

```bash
sudo apt install libpq-dev
```

Install the rest of the dependencies:

```bash
pip install -r requirements.txt
```

### Apple silicon

[Janus](https://github.com/wsg-ariadne/janus) uses TensorFlow, which at the time of writing is provided by the `tensorflow-macos` pip package on macOS running on Apple silicon.

This guide assumes you already have the Xcode command-line tools (`sudo xcode-select --install`). To install TensorFlow for Apple silicon with support for GPU via the Metal API,

1. Install [Miniforge](https://github.com/conda-forge/miniforge) either via the official installer or via Pyenv (`pyenv install miniforge3-latest`).
2. Create a new conda environment with `conda create -n tf-macos python=3.8`.
3. Activate the environment with `conda activate tf-macos`.
4. Install TensorFlow's dependencies with `conda install -c apple tensorflow-deps`.
5. Install TensorFlow with `pip install tensorflow-macos tensorflow-metal`.

Then install the rest of the dependencies with

```bash
pip install SQLAlchemy Flask Flask-SQLAlchemy flask-cors gunicorn nltk pandas pickle5 numpy opencv-python-headless psycopg2-binary
```

## Usage

Make sure you have a Postgres database set up. Take note of the username, password, hostname (if not `localhost`), and port.

Copy the `dionysus.conf.example` file as `dionysus.conf` and edit it to match your database configuration:

```
[database]
host=<postgres hostname>
port=<postgres port>
name=dionysus
user=<postgres username>
pass=<postgres password>

[dionysus]
debug=yes
api_prefix=/api/v1
enable_logger_middleware=no
; Comma-separated allowed origins for CORS
cors_origins=*
```

Dionysus is a Flask app, so you can run it with `flask run`:

```bash
FLASK_APP=main.py FLASK_DEBUG=1 python -m flask run
```

When in production, set `debug=no`, `enable_logger_middleware=no`, and `cors_origins` to the right domain(s) in `dionysus.conf`. It is recommended to use a proper WSGI server such as Gunicorn, which is included in the project dependencies.

```bash
python -m gunicorn
```

In both cases, Dionysus will be listening on port 5000.

## Deployment

It is recommended to use the Dionysus [Docker image](https://hub.docker.com/r/jareddantis/wsg-ariadne-dionysus), which contains all the dependencies and is ready to be deployed without manually setting up TensorFlow, NLTK, etc.

This image is built on every push to the `main` branch. You can also build it locally:

```bash
docker build -t jareddantis/wsg-ariadne-dionysus .
```

Refer to the `docker-compose.yml.example` file for an example Docker Compose configuration, which includes specifications for a Postgres container. Remember to create and mount the `dionysus.conf` configuration file into `/opt/app`.

## API

The default prefix is `/api/v1`; this can be changed in `dionysus.conf`. All endpoints expect and return JSON, except for the `<prefix>/healthcheck` route, which is used for Docker Compose health checks.

```bash
$ curl http://localhost:5000/api/v1/healthcheck
OK
```

| Endpoint | Method | Description |
| --- | --- | --- |
| `/healthcheck` | `GET` | Returns `OK` if the server is running. |
| `/classify/image` | `POST` | Classifies a cookie banner screencapture using Janus. Takes a JSON object with an `image_data` key whose value is a data URI containing a base64-encoded image. See [Classifier response objects](#classifier-response-objects) for the response format. |
| `/classify/text` | `POST` | Classifies cookie banner text using Calliope. Takes a JSON object with a `text` key. See [Classifier response objects](#classifier-response-objects) for the response format. |
| `/classify/report` | `POST` | Submits a report for *automatic* deceptive design detection. See [Classifier report and response object](#classifier-report-and-response-object) for the request and response formats. |
| `/reports` | `GET` | See [Reports summary object](#reports-summary-object). |
| `/reports` | `POST` | Submits a report for deceptive design patterns. Takes a JSON object with a `page_url` key and a [`deceptive_design_type`](#recognized-deceptive-design-types) key. |
| `/reports/by-id` | `POST` | Returns a report by its UUID. Takes a JSON object with a single key `report_id` with the requested UUID. See [Report object](#report-object) for the response format. |
| `/reports/by-url` | `POST` | Returns a summary of reports for a URL. Takes a JSON object with a single key `page_url` with the requested URL. See [URL report summary object](#url-report-summary-object) for the response format. |

### Recognized deceptive design types

These are the valid values for `deceptive_design_types` in the request body for `/report`, as well as the `deceptive_design_type` field in the response body for `/classify/image`.

| Value | Friendly name | Description |
| --- | --- | --- |
| `unclear_language` | `Unclear language` | The cookie banner does not explicitly or clearly ask for consent to use cookies. |
| `weighted_options` | `Weighted options` | The controls on the cookie banner are weighted, i.e., designed to bring more visual emphasis on one option over another. |
| `prefilled_options` | `Pre-filled options` | The cookie banner has options that were filled out for the user, e.g., pre-checked checkboxes for different types of cookies. |
| `other` | `Other` | Other types of deceptive design not included above. |

### Classifier response objects

The `POST /classify/image` endpoint returns a JSON object with the following keys:

```jsonc
{
    "success": true,

    // Predicted classification for the cookie banner image.
    //   'absent'     no cookie banner options detected
    //   'even'       cookie banner options detected, likely unweighted
    //   'weighted'   cookie banner options detected, likely weighted
    "classification": "absent"
}
```

The `POST /classify/text` endpoint returns a JSON object with the following keys:

```jsonc
{
    "success": true,

    // Whether the language used in the cookie banner text
    // is 'good' (likely not deceptive) or 'bad' (likely deceptive)
    "is_good": true
}
```

### Classifier report and response object

The `POST /classify/report` endpoint expects a JSON object with the following keys:

```jsonc
{
    // URL of the page where the cookie banner was found
    "page_url": "http://example.com",

    // Whether the cookie banner used unclear language or not
    "calliope_tripped": true,

    // Janus's classification for the cookie banner
    // See (#classifier-response-objects) for the possible values
    "janus_result": "weighted",

    // Whether the user verified the classification as correct or not
    "vote": true,

    // Optional:
    // The cookie banner text that was submitted to /classify/text
    "calliope_text": "We use cookies on this site...",

    // Optional:
    // The cookie banner image that was submitted to /classify/image,
    // in data URI format
    "janus_screenshot": "data:image/png;base64,...",

    // Optional: User remarks
    "remarks": "This cookie banner is deceptive because..."
}
```

The endpoint will then return a JSON object with the following keys:

```jsonc
{
    // UUID of the detection report
    "detection_id": "9d852b6b-c20c-49e6-909d-c8529fae3773",
    "success": true
}
```

### Reports summary object

The `GET /reports` endpoint returns a JSON object with the following keys:

```jsonc
{
    // When this is false, the other keys are not present
    // and an `error` key is present instead.
    "success" : true,

    // Total number of unique reports in the database
    "total_reports": 1,

    // Number of unique domains for which there are reports
    "num_domains": 1,

    // Statistics for the most-reported domain
    "top_domain": {
        "domain": "example.com",

        // Number of reports for this domain
        "num_reports": 1,

        // Number of reports for this domain per type
        // The keys are the same as the **friendly names** for `deceptive_design_type`
        "per_type": {
            "Unclear language": 1,
            "Pre-filled options": 0,
            "Weighted options": 0,
            "Other": 0
        },
    },

    // Five most recent reports
    "most_recent_reports": [
        {
            // Report UUID
            "id": "9d852b6b-c20c-49e6-909d-c8529fae3773",

            // Website being reported
            "domain": "example.com",
            "path": "/example",

            // Report details
            // Values are the same as the **friendly names** for `deceptive_design_type`,
            // except when `is_custom_type` is true
            "deceptive_design_type": "Unclear language",
            "is_custom_type": false,

            // Number of times this report was submitted,
            // and the date and time the report was last submitted
            // This means that multiple reports for the same domain and path
            // will be grouped together into one UUID
            "num_reports": 1,
            "last_report_timestamp": 1683054243184.512
        }
    ]
}
```

### Report object

The `POST /reports/by-id` endpoint returns a JSON object with the following keys:

```jsonc
{
    "success": true,
    "report": {
        // Report UUID
        "id": "9d852b6b-c20c-49e6-909d-c8529fae3773",

        // Website being reported
        "domain": "example.com",
        "path": "/example",

        // Report details
        // Values are the same as the **friendly names** for `deceptive_design_type`,
        // except when `is_custom_type` is true
        "deceptive_design_type": "Unclear language",
        "is_custom_type": false,

        // Number of times this report was submitted,
        // and the date and time the report was first and last submitted
        // This means that multiple reports for the same domain and path
        // will be grouped together into one UUID
        "num_reports": 1,
        "first_report_timestamp": 1683054243184.512,
        "last_report_timestamp": 1683054243184.512
    }
}
```

### URL report summary object

The `POST /reports/by-url` endpoint returns a JSON object with the following keys:

```jsonc
{
    "success": true,

    // Statistics for this domain AND url (exact match)
    "specific_reports": {
        "count": 1,
        "last_report_timestamp": 1683054243184.512,
        "by_type": {
            "other": 0,
            "prefilled_options": 0,
            "unclear_language": 1,
            "weighted_options": 1
        }
    },

    // Statistics for this domain (any url)
    "general_reports": {
        "count": 1,
        "last_report_timestamp": 1683054243184.512
    }
}
```
