from flask import Blueprint, request
from classifiers import CALLIOPE_MODEL, JANUS_MODEL, JANUS_CLASSIFICATIONS


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
