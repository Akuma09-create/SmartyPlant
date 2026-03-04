"""
History routes for plant analysis history management.
"""

import io
from flask import Blueprint, request, jsonify, g, send_file
from auth import login_required, login_optional
from models.database_models import db, PlantAnalysis, AnalysisHistory

# Create blueprint
history_routes = Blueprint('history', __name__, url_prefix='/api/v1')


@history_routes.route('/history', methods=['GET'])
@login_optional
def get_history():
    """
    Get analysis history for current user.
    
    Query params:
        limit (int, optional): Maximum items to return (default 50)
    
    Response:
        success (bool): Operation success
        history (list): List of analysis history items
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)
        
        user_id = getattr(g, 'user_id', None)
        
        if user_id:
            # Get from PlantAnalysis table
            analyses = PlantAnalysis.query.filter_by(user_id=user_id)\
                .order_by(PlantAnalysis.created_at.desc())\
                .limit(limit)\
                .all()
            
            history = [{
                'id': a.id,
                'plant_name': a.plant_type,
                'image_url': a.image_filename,
                'health_score': a.health_score,
                'diagnosis': a.disease_detected,
                'analysis_result': a.analysis_details,
                'language': a.language,
                'created_at': a.created_at.isoformat() if a.created_at else None
            } for a in analyses]
        else:
            history = []
        
        return jsonify({
            'success': True,
            'history': history
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@history_routes.route('/history/<int:analysis_id>', methods=['GET'])
@login_optional
def get_analysis(analysis_id):
    """
    Get a specific analysis.
    
    Response:
        success (bool): Operation success
        analysis (dict): Analysis data
    """
    try:
        user_id = getattr(g, 'user_id', None)
        
        analysis = PlantAnalysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
        
        # Check ownership if user is logged in
        if user_id and analysis.user_id and analysis.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        return jsonify({
            'success': True,
            'analysis': {
                'id': analysis.id,
                'plant_name': analysis.plant_type,
                'image_url': analysis.image_filename,
                'health_score': analysis.health_score,
                'diagnosis': analysis.disease_detected,
                'analysis_result': analysis.analysis_details,
                'language': analysis.language,
                'created_at': analysis.created_at.isoformat() if analysis.created_at else None
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@history_routes.route('/history/<int:analysis_id>', methods=['DELETE'])
@login_required
def delete_analysis(analysis_id):
    """
    Delete an analysis.
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        analysis = PlantAnalysis.query.filter_by(
            id=analysis_id, 
            user_id=g.user_id
        ).first()
        
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
        
        # Delete associated image file if exists
        if analysis.image_filename:
            import os
            from flask import current_app
            try:
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                filename = analysis.image_filename.replace('/uploads/', '')
                filepath = os.path.join(upload_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass
        
        db.session.delete(analysis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Analysis deleted'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@history_routes.route('/history/<int:analysis_id>/report', methods=['GET'])
@login_optional
def download_report(analysis_id):
    """
    Download analysis report as PDF or image.
    
    Query params:
        format (str): Report format - 'pdf' or 'image' (default: pdf)
        language (str): Report language (default: en)
    
    Response:
        File download (PDF or PNG)
    """
    try:
        user_id = getattr(g, 'user_id', None)
        
        analysis = PlantAnalysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
        
        # Check ownership if user is logged in and analysis has owner
        if user_id and analysis.user_id and analysis.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        report_format = request.args.get('format', 'pdf').lower()
        language = request.args.get('language', 'en')
        
        # Prepare analysis data for report
        import json
        analysis_result = analysis.analysis_details
        if isinstance(analysis_result, str):
            try:
                analysis_result = json.loads(analysis_result)
            except:
                analysis_result = {'summary': analysis_result}
        
        analysis_data = {
            'id': analysis.id,
            'plant_name': analysis.plant_type or 'Unknown Plant',
            'health_score': analysis.health_score,
            'diagnosis': analysis.disease_detected,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
            **analysis_result
        }
        
        # Import report service
        from services.report_service import report_service
        
        if report_format == 'image':
            # Generate image report
            image_bytes = report_service.generate_image_report(
                analysis_data, language
            )
            
            if image_bytes:
                return send_file(
                    io.BytesIO(image_bytes),
                    mimetype='image/png',
                    as_attachment=True,
                    download_name=f'plant-analysis-{analysis_id}.png'
                )
        else:
            # Generate PDF report
            pdf_bytes = report_service.generate_pdf_report(
                analysis_data, language
            )
            
            if pdf_bytes:
                return send_file(
                    io.BytesIO(pdf_bytes),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'plant-analysis-{analysis_id}.pdf'
                )
        
        return jsonify({
            'success': False,
            'error': 'Failed to generate report'
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
