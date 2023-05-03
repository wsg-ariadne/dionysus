from flask import Blueprint, request
from classifiers import CALLIOPE_MODEL


# Create Flask blueprint
bp_classify = Blueprint('classify', __name__)

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
