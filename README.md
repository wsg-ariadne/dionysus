dionysus
===

REST API for the Ariadne project. Takes care of the database and the classifiers Calliope and Janus.

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

## API

The default prefix is `/api/v1`; this can be changed in `dionysus.conf`. All endpoints expect and return JSON, except for the `<prefix>/healthcheck` route, which is used for Docker Compose health checks.

```bash
$ curl http://localhost:5000/api/v1/healthcheck
OK
```

| Endpoint | Method | Description |
| --- | --- | --- |
| `/healthcheck` | `GET` | Returns `OK` if the server is running. |
| `/classify/image` | `POST` | Classifies a cookie banner screencapture using Janus. Takes a JSON object with an `image_data` key whose value is a data URI containing a base64-encoded image. |
| `/classify/text` | `POST` | Classifies cookie banner text using Calliope. Takes a JSON object with a `text` key. See [Classifier response object](#classifier-response-object) for the response format. |
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

### Classifier response object

The `POST /classify/text` endpoint returns a JSON object with the following keys:

```json
{
    "success": true,

    // Whether the language used in the cookie banner text
    // is 'good' (likely not deceptive) or 'bad' (likely deceptive)
    "is_good": true
}
```

### Reports summary object

The `GET /reports` endpoint returns a JSON object with the following keys:

```json
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

```json
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

```json
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
