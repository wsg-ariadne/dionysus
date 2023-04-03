from database import db
from datetime import datetime
from flask import Blueprint, request
from models import VALID_DESIGN_TYPES
from models.report import Report
from typing import List
from urllib.parse import urlparse


bp_report = Blueprint('report', __name__)


@bp_report.route('/report', methods=['POST'])
def submit_report():
    # Check request body
    try:
        page_url = request.json['page_url']
        deceptive_design_types = request.json['deceptive_design_types']
        
        # Check that deceptive_design_types is a non-empty list
        if not isinstance(deceptive_design_types, List) or len(deceptive_design_types) == 0:
            raise KeyError

        # Save custom_deceptive_design_type if 'other' is in deceptive_design_types
        if 'other' in deceptive_design_types:
            custom_deceptive_design_type = request.json['custom_deceptive_design_type']
    except KeyError:
        return {
            'success': False,
            'error': 'Missing or invalid required field'
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
    
    # Check if deceptive_design_types are valid
    for deceptive_design_type in deceptive_design_types:
        if deceptive_design_type not in VALID_DESIGN_TYPES:
            return {
                'success': False,
                'error': 'Invalid deceptive design type'
            }, 400
    
    # Iterate through each deceptive design type and create a report
    reports = {}
    for deceptive_design_type in deceptive_design_types:
        design_type = deceptive_design_type
        is_custom_type = False
        if design_type == 'other':
            is_custom_type = True
            design_type = custom_deceptive_design_type
        
        # Create report if it doesn't exist
        report = Report.query.filter_by(
            domain=domain,
            path=path,
            deceptive_design_type=design_type,
            is_custom_type=is_custom_type
        ).first()
        if not report:
            existing = 1
            report = Report(
                domain=domain,
                path=path,
                deceptive_design_type=design_type,
                is_custom_type=is_custom_type,
                num_reports=1,
                last_report_timestamp=datetime.utcnow()
            )
            db.session.add(report)
        # Otherwise, increment num_reports
        else:
            existing = report.num_reports + 1
            report.num_reports = existing
            report.last_report_timestamp = datetime.utcnow()
        
        # Save changes to database
        db.session.commit()

        # Get report ID
        reports[deceptive_design_type] = {
            'id': report.id,
            'existing_reports': existing
        }
    
    # Return report IDs
    return {
        'success': True,
        'reports': reports
    }, 200
    