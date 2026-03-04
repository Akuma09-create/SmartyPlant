"""
Treatment routes for Smart Plant Health Assistant.
Handles treatment CRUD operations and progress tracking.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
import json

from auth import login_required
from models.database_models import db, Treatment, Reminder, Plant, PlantAnalysis

# Create blueprint
treatment_routes = Blueprint('treatments', __name__, url_prefix='/api/v1/treatments')


# ============================================================================
# Treatment CRUD Operations
# ============================================================================

@treatment_routes.route('', methods=['GET'])
@login_required
def get_treatments():
    """
    Get all treatments for the current user.
    
    Query params:
        status (str): Filter by status (active, completed, abandoned)
        plant_id (int): Filter by plant
    
    Response:
        success (bool)
        treatments (list): List of treatment objects
    """
    try:
        user_id = g.user_id
        
        # Build query
        query = Treatment.query.filter_by(user_id=user_id)
        
        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        plant_id = request.args.get('plant_id')
        if plant_id:
            query = query.filter_by(plant_id=int(plant_id))
        
        # Order by most recent first
        treatments = query.order_by(Treatment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'treatments': [t.to_dict() for t in treatments],
            'total': len(treatments)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching treatments: {str(e)}'
        }), 500


@treatment_routes.route('/<int:treatment_id>', methods=['GET'])
@login_required
def get_treatment(treatment_id):
    """
    Get a specific treatment by ID.
    
    Response:
        success (bool)
        treatment (dict): Treatment details
    """
    try:
        user_id = g.user_id
        
        treatment = Treatment.query.filter_by(
            id=treatment_id,
            user_id=user_id
        ).first()
        
        if not treatment:
            return jsonify({
                'success': False,
                'message': 'Treatment not found'
            }), 404
        
        # Include related plant and analysis info
        result = treatment.to_dict()
        
        if treatment.plant_id:
            plant = Plant.query.get(treatment.plant_id)
            if plant:
                result['plant'] = plant.to_dict()
        
        if treatment.analysis_id:
            analysis = PlantAnalysis.query.get(treatment.analysis_id)
            if analysis:
                result['analysis'] = analysis.to_dict()
        
        return jsonify({
            'success': True,
            'treatment': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching treatment: {str(e)}'
        }), 500


@treatment_routes.route('', methods=['POST'])
@login_required
def create_treatment():
    """
    Create a new treatment plan from an analysis.
    
    Request JSON:
        analysis_id (int): The analysis this treatment is based on
        plant_id (int, optional): Link to an existing plant
        treatment_type (str): organic, chemical, or cultural
        disease_name (str): Name of the disease being treated
        severity (str): mild, moderate, or severe
        steps (list): List of treatment step objects
        estimated_duration_days (int, optional): Expected treatment duration
        create_reminders (bool, optional): Auto-create treatment reminders
    
    Response:
        success (bool)
        treatment (dict): Created treatment
        message (str)
    """
    try:
        user_id = g.user_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        # Validate required fields
        disease_name = data.get('disease_name', '').strip()
        treatment_type = data.get('treatment_type', '').strip()
        steps = data.get('steps', [])
        
        if not disease_name:
            return jsonify({
                'success': False,
                'message': 'Disease name is required'
            }), 400
        
        if treatment_type not in ['organic', 'chemical', 'cultural']:
            return jsonify({
                'success': False,
                'message': 'Treatment type must be organic, chemical, or cultural'
            }), 400
        
        if not steps or not isinstance(steps, list):
            return jsonify({
                'success': False,
                'message': 'Treatment steps are required'
            }), 400
        
        # Format steps with completion status
        formatted_steps = []
        for i, step in enumerate(steps):
            if isinstance(step, str):
                formatted_steps.append({
                    'step': i + 1,
                    'description': step,
                    'completed': False,
                    'completed_at': None
                })
            elif isinstance(step, dict):
                formatted_steps.append({
                    'step': i + 1,
                    'description': step.get('description', step.get('step', f'Step {i+1}')),
                    'completed': False,
                    'completed_at': None
                })
        
        # Create treatment
        treatment = Treatment(
            user_id=user_id,
            plant_id=data.get('plant_id'),
            analysis_id=data.get('analysis_id'),
            disease_name=disease_name,
            treatment_type=treatment_type,
            severity=data.get('severity', 'moderate'),
            steps=json.dumps(formatted_steps),
            total_steps=len(formatted_steps),
            current_step=0,
            progress_percent=0.0,
            status='active',
            estimated_duration_days=data.get('estimated_duration_days'),
            notes=data.get('notes')
        )
        
        db.session.add(treatment)
        db.session.flush()  # Get the treatment ID
        
        # Create treatment reminders if requested
        if data.get('create_reminders', True):
            _create_treatment_reminders(treatment, user_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Treatment plan created successfully',
            'treatment': treatment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error creating treatment: {str(e)}'
        }), 500


@treatment_routes.route('/<int:treatment_id>/progress', methods=['PUT'])
@login_required
def update_progress(treatment_id):
    """
    Update treatment progress - mark steps as completed.
    
    Request JSON:
        step_index (int): The step index to update (0-based)
        completed (bool): Whether the step is completed
    
    Response:
        success (bool)
        treatment (dict): Updated treatment
    """
    try:
        user_id = g.user_id
        data = request.get_json()
        
        treatment = Treatment.query.filter_by(
            id=treatment_id,
            user_id=user_id
        ).first()
        
        if not treatment:
            return jsonify({
                'success': False,
                'message': 'Treatment not found'
            }), 404
        
        if treatment.status != 'active':
            return jsonify({
                'success': False,
                'message': 'Cannot update a completed or abandoned treatment'
            }), 400
        
        step_index = data.get('step_index')
        completed = data.get('completed', True)
        
        if step_index is None:
            return jsonify({
                'success': False,
                'message': 'Step index is required'
            }), 400
        
        # Parse and update steps
        steps = json.loads(treatment.steps) if isinstance(treatment.steps, str) else treatment.steps
        
        if step_index < 0 or step_index >= len(steps):
            return jsonify({
                'success': False,
                'message': 'Invalid step index'
            }), 400
        
        steps[step_index]['completed'] = completed
        steps[step_index]['completed_at'] = datetime.utcnow().isoformat() if completed else None
        
        treatment.steps = json.dumps(steps)
        treatment.update_progress()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated',
            'treatment': treatment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating progress: {str(e)}'
        }), 500


@treatment_routes.route('/<int:treatment_id>/complete', methods=['POST'])
@login_required
def complete_treatment(treatment_id):
    """
    Mark a treatment as completed.
    
    Response:
        success (bool)
        treatment (dict): Updated treatment
    """
    try:
        user_id = g.user_id
        
        treatment = Treatment.query.filter_by(
            id=treatment_id,
            user_id=user_id
        ).first()
        
        if not treatment:
            return jsonify({
                'success': False,
                'message': 'Treatment not found'
            }), 404
        
        treatment.status = 'completed'
        treatment.completed_at = datetime.utcnow()
        treatment.progress_percent = 100.0
        
        # Mark all steps as completed
        steps = json.loads(treatment.steps) if isinstance(treatment.steps, str) else treatment.steps
        for step in steps:
            if not step.get('completed'):
                step['completed'] = True
                step['completed_at'] = datetime.utcnow().isoformat()
        treatment.steps = json.dumps(steps)
        treatment.current_step = treatment.total_steps
        
        # Disable treatment reminders
        Reminder.query.filter_by(
            treatment_id=treatment_id,
            user_id=user_id
        ).update({'enabled': False})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Treatment marked as completed',
            'treatment': treatment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error completing treatment: {str(e)}'
        }), 500


@treatment_routes.route('/<int:treatment_id>/abandon', methods=['POST'])
@login_required
def abandon_treatment(treatment_id):
    """
    Abandon a treatment plan.
    
    Request JSON:
        reason (str, optional): Reason for abandoning
    
    Response:
        success (bool)
        treatment (dict): Updated treatment
    """
    try:
        user_id = g.user_id
        data = request.get_json(silent=True) or {}
        
        treatment = Treatment.query.filter_by(
            id=treatment_id,
            user_id=user_id
        ).first()
        
        if not treatment:
            return jsonify({
                'success': False,
                'message': 'Treatment not found'
            }), 404
        
        treatment.status = 'abandoned'
        
        if data.get('reason'):
            treatment.notes = (treatment.notes or '') + f"\nAbandoned: {data['reason']}"
        
        # Disable treatment reminders
        Reminder.query.filter_by(
            treatment_id=treatment_id,
            user_id=user_id
        ).update({'enabled': False})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Treatment abandoned',
            'treatment': treatment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error abandoning treatment: {str(e)}'
        }), 500


@treatment_routes.route('/<int:treatment_id>', methods=['DELETE'])
@login_required
def delete_treatment(treatment_id):
    """
    Delete a treatment plan.
    
    Response:
        success (bool)
        message (str)
    """
    try:
        user_id = g.user_id
        
        treatment = Treatment.query.filter_by(
            id=treatment_id,
            user_id=user_id
        ).first()
        
        if not treatment:
            return jsonify({
                'success': False,
                'message': 'Treatment not found'
            }), 404
        
        # Delete associated reminders
        Reminder.query.filter_by(treatment_id=treatment_id).delete()
        
        db.session.delete(treatment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Treatment deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting treatment: {str(e)}'
        }), 500


@treatment_routes.route('/active', methods=['GET'])
@login_required
def get_active_treatments():
    """
    Get count and summary of active treatments.
    
    Response:
        success (bool)
        active_count (int)
        treatments (list): Brief treatment summaries
    """
    try:
        user_id = g.user_id
        
        treatments = Treatment.query.filter_by(
            user_id=user_id,
            status='active'
        ).order_by(Treatment.created_at.desc()).all()
        
        summaries = []
        for t in treatments:
            summaries.append({
                'id': t.id,
                'disease_name': t.disease_name,
                'treatment_type': t.treatment_type,
                'progress_percent': t.progress_percent,
                'current_step': t.current_step,
                'total_steps': t.total_steps,
                'plant_id': t.plant_id,
                'started_at': t.started_at.isoformat() if t.started_at else None
            })
        
        return jsonify({
            'success': True,
            'active_count': len(treatments),
            'treatments': summaries
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching active treatments: {str(e)}'
        }), 500


# ============================================================================
# Helper Functions
# ============================================================================

def _create_treatment_reminders(treatment, user_id):
    """Create reminders for treatment steps."""
    try:
        steps = json.loads(treatment.steps) if isinstance(treatment.steps, str) else treatment.steps
        
        # Calculate frequency based on estimated duration and number of steps
        duration_days = treatment.estimated_duration_days or 14
        if len(steps) > 1:
            frequency = max(1, duration_days // len(steps))
        else:
            frequency = 7
        
        # Create a reminder for the treatment
        reminder = Reminder(
            user_id=user_id,
            plant_id=treatment.plant_id,
            treatment_id=treatment.id,
            type='treatment',
            title=f"Treatment: {treatment.disease_name}",
            frequency_days=frequency,
            next_due=datetime.utcnow() + timedelta(days=frequency),
            enabled=True
        )
        db.session.add(reminder)
        
    except Exception as e:
        print(f"Error creating treatment reminders: {e}")
