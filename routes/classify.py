from classifiers import CALLIOPE_MODEL, JANUS_MODEL, JANUS_CLASSIFICATIONS
from database import db
from flask import Blueprint, request
from models.detection import Detection
from urllib.parse import urlparse


# Create Flask blueprint
bp_classify = Blueprint('classify', __name__)

# Route for classifying image
@bp_classify.route('/image', methods=['POST'])
def classify_image():
    # Get image data from request body
    try:
        img_uri = request.json['image_data']
    except KeyError:
        return {
            'success': False,
            'error': 'Missing image_data in request body'
        }, 400
    
    # Classify image
    return {
        'success': True,
        'classification': JANUS_CLASSIFICATIONS[JANUS_MODEL.classify(img_uri)]
    }, 200

# Route for classifying text
@bp_classify.route('/text', methods=['POST'])
def classify_text():
    # Get text from request body
    try:
        text = request.json['text']
    except KeyError:
        return {
            'success': False,
            'error': 'Missing text in request body'
        }, 400
    
    # Classify text
    return {
        'success': True,
        'is_good': CALLIOPE_MODEL.classify(text)
    }, 200

# Route for saving classification reports
@bp_classify.route('/report', methods=['POST'])
def report_classification():
    # Get required data from request body
    try:
        page_url = request.json['page_url']
        vote = request.json['vote']
        calliope_tripped = request.json.get('calliope_tripped', None)
        janus_result = request.json.get('janus_result', None)
        calliope_text = request.json.get('calliope_text', None)
        janus_screenshot = request.json.get('janus_screenshot', None)
        remarks = request.json.get('remarks', None)

        # janus_result must be in JANUS_CLASSIFICATIONS
        if janus_result is not None and janus_result not in JANUS_CLASSIFICATIONS.values():
            raise ValueError
        
        # calliope_tripped must be Boolean
        if calliope_tripped is not None and not isinstance(calliope_tripped, bool):
            raise ValueError

        # vote must be Boolean
        if not isinstance(vote, bool):
            raise ValueError
    except KeyError:
        return {
            'success': False,
            'error': 'Missing data in request body'
        }, 400
    except ValueError:
        return {
            'success': False,
            'error': 'Invalid data in request body'
        }, 400
    
    # Check if page_url is valid
    try:
        parsed_url = urlparse(page_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError
    except ValueError:
        return {
            'success': False,
            'error': 'Invalid URL'
        }, 400
    else:
        # Extract domain and path from URL
        domain = parsed_url.netloc
        path = parsed_url.path
    
    print(remarks)
    
    # Get key in JANUS_CLASSIFICATIONS for janus_result
    janus_result_int = None
    if janus_result is not None:
        janus_result_int = list(JANUS_CLASSIFICATIONS.keys())[list(JANUS_CLASSIFICATIONS.values()).index(janus_result)]
    
    # Save report to database
    detection = Detection(
        domain=domain,
        path=path,
        calliope_tripped=calliope_tripped,
        janus_result=janus_result_int,
        calliope_text=calliope_text,
        janus_screenshot=janus_screenshot,
        vote=vote,
        remarks=remarks
    )
    db.session.add(detection)
    db.session.commit()

    # Get detection ID
    detection_id = detection.id

    # Return success
    return {
        'success': True,
        'detection_id': detection_id
    }, 200
