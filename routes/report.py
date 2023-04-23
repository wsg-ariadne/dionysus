from database import db
from datetime import datetime
from flask import Blueprint, request
from models import FRIENDLY_DESIGN_TYPES, VALID_DESIGN_TYPES
from models.report import Report
from sqlalchemy.sql import func
from typing import List
from urllib.parse import urlparse


bp_report = Blueprint('report', __name__)


@bp_report.route('', methods=['POST'])
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


@bp_report.route('', methods=['GET'])
def get_reports():
    # Check if there are any reports
    reports = Report.query.order_by(Report.last_report_timestamp.desc()).all()
    if not reports:
        return {
            'success': False,
            'error': 'No reports found'
        }, 404
    
    # Get sum of num_reports column
    total_reports = Report.query.with_entities(func.sum(Report.num_reports)).scalar()

    # Get unique domains
    domains = Report.query.with_entities(Report.domain).distinct()

    # Get sum of num_reports column per domain
    grouped = Report.query.with_entities(
        Report.domain,
        func.sum(Report.num_reports)
    ).group_by(Report.domain).all()
    top_domain = max(grouped, key=lambda x: x[1])
    top_domain_name = top_domain[0]
    top_domain_count = top_domain[1]
    
    # Get sum of num_reports column per deceptive_design_type for most reported domain
    grouped = Report.query.with_entities(
        Report.deceptive_design_type,
        func.sum(Report.num_reports)
    ).filter_by(domain=top_domain_name).group_by(Report.deceptive_design_type).all()
    count_per_type = { FRIENDLY_DESIGN_TYPES[x]: 0 for x in VALID_DESIGN_TYPES }
    for group in grouped:
        design_type = group[0]
        if design_type not in VALID_DESIGN_TYPES:
            design_type = 'other'
        
        count_per_type[FRIENDLY_DESIGN_TYPES[design_type]] += group[1]
    
    # Return
    return {
        'success': True,
        'total_reports': total_reports,
        'num_domains': domains.count(),
        'top_domain': {
            'domain': top_domain_name,
            'num_reports': top_domain_count,
            'per_type': count_per_type
        },
        'most_recent_reports': [
            {
                'id': report.id,
                'domain': report.domain,
                'path': report.path,
                'deceptive_design_type': report.deceptive_design_type if report.is_custom_type else FRIENDLY_DESIGN_TYPES[report.deceptive_design_type],
                'is_custom_type': report.is_custom_type,
                'num_reports': report.num_reports,
                'last_report_timestamp': report.last_report_timestamp.timestamp() * 1000
            } for report in reports[-5:]
        ]
    }, 200


@bp_report.route('/by-id', methods=['POST'])
def get_report():
    # Check request body
    try:
        report_id = request.json['report_id']
    except KeyError:
        return {
            'success': False,
            'error': 'Missing report ID'
        }, 400
    
    # Get report
    report = Report.query.filter_by(id=report_id).first()
    if not report:
        return {
            'success': False,
            'error': 'Report not found'
        }, 404
    
    # Return report
    return {
        'success': True,
        'report': {
            'id': report.id,
            'domain': report.domain,
            'path': report.path,
            'deceptive_design_type': FRIENDLY_DESIGN_TYPES[report.deceptive_design_type],
            'is_custom_type': report.is_custom_type,
            'num_reports': report.num_reports,
            'last_report_timestamp': report.last_report_timestamp.timestamp() * 1000
        }
    }, 200


@bp_report.route('/by-url', methods=['POST'])
def get_report_by_url():
    # Check request body
    try:
        page_url = request.json['page_url']
    except KeyError:
        return {
            'success': False,
            'error': 'Missing page URL'
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
    
    # Get reports sorted by last_report_timestamp
    specific_reports = Report.query.filter_by(domain=domain, path=path).order_by(Report.last_report_timestamp.desc())
    general_reports = Report.query.filter_by(domain=domain).order_by(Report.last_report_timestamp.desc())
    
    # Get specific reports for each deceptive design type, sorted by last_report_timestamp
    specific_reports_by_type = { design_type: 0 for design_type in VALID_DESIGN_TYPES }
    for report in specific_reports:
        if report.is_custom_type:
            specific_reports_by_type['other'] += 1
        else:
            try:
                specific_reports_by_type[report.deceptive_design_type] = 1
            except KeyError:
                print('Invalid design type: ' + report.deceptive_design_type)
                specific_reports_by_type['other'] += 1

    # Return counts
    return {
        'success': True,
        'specific_reports': {
            'count': specific_reports.count(),
            'last_report_timestamp': specific_reports.first().last_report_timestamp.timestamp() * 1000 if specific_reports.first() else None,
            'by_type': specific_reports_by_type
        },
        'general_reports': {
            'count': general_reports.count(),
            'last_report_timestamp': general_reports.first().last_report_timestamp.timestamp() * 1000 if general_reports.first() else None,
        }
    }, 200
