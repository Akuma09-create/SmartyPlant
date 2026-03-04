"""
Plant management routes.
CRUD operations for user's plants.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.utils import secure_filename
from auth import login_required
from models.database_models import db, Plant, Reminder

# Create blueprint
plant_routes = Blueprint('plants', __name__, url_prefix='/api/v1')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Load plant care defaults
_care_defaults = None

def get_care_defaults():
    """Load plant care defaults from JSON file."""
    global _care_defaults
    if _care_defaults is None:
        try:
            defaults_path = Path(__file__).parent.parent / 'data' / 'plant_care_defaults.json'
            with open(defaults_path, 'r') as f:
                _care_defaults = json.load(f)
        except Exception as e:
            print(f"Error loading care defaults: {e}")
            _care_defaults = {"care_defaults": {"general": {"watering_days": 7, "fertilizing_days": 30, "pruning_months": [3, 9], "repot_months": 24}}, "species_mapping": {}}
    return _care_defaults

def get_care_schedule_for_species(species):
    """Get care schedule based on species name."""
    defaults = get_care_defaults()
    
    if not species:
        return defaults['care_defaults']['general']
    
    species_lower = species.lower().strip()
    
    # Check species mapping
    for key, plant_type in defaults.get('species_mapping', {}).items():
        if key in species_lower or species_lower in key:
            return defaults['care_defaults'].get(plant_type, defaults['care_defaults']['general'])
    
    # Default to general care
    return defaults['care_defaults']['general']

def create_plant_care_reminders(plant, user_id):
    """Create full care schedule reminders for a plant."""
    care = get_care_schedule_for_species(plant.species)
    now = datetime.utcnow()
    reminders_created = []
    
    # Water reminder
    water_reminder = Reminder(
        user_id=user_id,
        plant_id=plant.id,
        type='water',
        title=f"Water {plant.name}",
        frequency_days=care.get('watering_days', 7),
        next_due=now + timedelta(days=care.get('watering_days', 7)),
        enabled=True
    )
    db.session.add(water_reminder)
    reminders_created.append('water')
    
    # Fertilize reminder
    fertilize_reminder = Reminder(
        user_id=user_id,
        plant_id=plant.id,
        type='fertilize',
        title=f"Fertilize {plant.name}",
        frequency_days=care.get('fertilizing_days', 30),
        next_due=now + timedelta(days=care.get('fertilizing_days', 30)),
        enabled=True
    )
    db.session.add(fertilize_reminder)
    reminders_created.append('fertilize')
    
    # Prune reminder (seasonal - next occurrence)
    pruning_months = care.get('pruning_months', [3, 9])
    if pruning_months:
        current_month = now.month
        next_prune_month = None
        for month in sorted(pruning_months):
            if month > current_month:
                next_prune_month = month
                break
        if next_prune_month is None:
            next_prune_month = pruning_months[0]
            year = now.year + 1
        else:
            year = now.year
        
        next_prune_date = datetime(year, next_prune_month, 15)
        
        prune_reminder = Reminder(
            user_id=user_id,
            plant_id=plant.id,
            type='prune',
            title=f"Prune {plant.name}",
            frequency_days=90,  # Quarterly check
            next_due=next_prune_date,
            enabled=True
        )
        db.session.add(prune_reminder)
        reminders_created.append('prune')
    
    # Repot reminder (based on months until repot)
    repot_months = care.get('repot_months', 24)
    repot_reminder = Reminder(
        user_id=user_id,
        plant_id=plant.id,
        type='repot',
        title=f"Repot {plant.name}",
        frequency_days=repot_months * 30,
        next_due=now + timedelta(days=repot_months * 30),
        enabled=True
    )
    db.session.add(repot_reminder)
    reminders_created.append('repot')
    
    return reminders_created


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@plant_routes.route('/plants', methods=['GET'])
@login_required
def get_plants():
    """
    Get all plants for current user.
    
    Query params:
        limit (int, optional): Maximum plants to return
    
    Response:
        success (bool): Operation success
        plants (list): List of plants
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        
        plants = Plant.query.filter_by(user_id=g.user_id)\
            .order_by(Plant.created_at.desc())\
            .limit(limit)\
            .all()
        
        plants_data = []
        for plant in plants:
            plant_dict = plant.to_dict()
            # Get reminders for this plant
            reminders = Reminder.query.filter_by(plant_id=plant.id).all()
            plant_dict['reminders'] = [r.to_dict() for r in reminders]
            plants_data.append(plant_dict)
        
        return jsonify({
            'success': True,
            'plants': plants_data
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants/<int:plant_id>', methods=['GET'])
@login_required
def get_plant(plant_id):
    """
    Get a specific plant.
    
    Response:
        success (bool): Operation success
        plant (dict): Plant data
    """
    try:
        plant = Plant.query.filter_by(id=plant_id, user_id=g.user_id).first()
        
        if not plant:
            return jsonify({
                'success': False,
                'error': 'Plant not found'
            }), 404
        
        plant_dict = plant.to_dict()
        # Get reminders for this plant
        reminders = Reminder.query.filter_by(plant_id=plant.id).all()
        plant_dict['reminders'] = [r.to_dict() for r in reminders]
        
        return jsonify({
            'success': True,
            'plant': plant_dict
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants', methods=['POST'])
@login_required
def create_plant():
    """
    Create a new plant.
    
    Request (form-data):
        name (str, required): Plant name
        species (str, optional): Plant species
        location (str, optional): Plant location
        notes (str, optional): Notes about the plant
        image (file, optional): Plant image
    
    Response:
        success (bool): Operation success
        plant (dict): Created plant
    """
    try:
        name = request.form.get('name', '').strip()
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Plant name is required'
            }), 400
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                import uuid
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Ensure uploads directory exists
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                filepath = os.path.join(upload_dir, unique_filename)
                file.save(filepath)
                image_url = f"/uploads/{unique_filename}"
        
        # Create plant
        plant = Plant(
            user_id=g.user_id,
            name=name,
            species=request.form.get('species', '').strip() or None,
            location=request.form.get('location', '').strip() or None,
            notes=request.form.get('notes', '').strip() or None,
            image_filename=image_url
        )
        
        db.session.add(plant)
        db.session.flush()  # Get the plant ID
        
        # Create automatic care reminders based on species
        reminders_created = create_plant_care_reminders(plant, g.user_id)
        
        db.session.commit()
        
        plant_dict = plant.to_dict()
        plant_dict['reminders_created'] = reminders_created
        
        return jsonify({
            'success': True,
            'plant': plant_dict,
            'message': f'Plant created with {len(reminders_created)} care reminders'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants/<int:plant_id>', methods=['PUT'])
@login_required
def update_plant(plant_id):
    """
    Update a plant.
    
    Request JSON:
        name (str, optional): Plant name
        species (str, optional): Plant species
        location (str, optional): Plant location
        notes (str, optional): Notes about the plant
    
    Response:
        success (bool): Operation success
        plant (dict): Updated plant
    """
    try:
        plant = Plant.query.filter_by(id=plant_id, user_id=g.user_id).first()
        
        if not plant:
            return jsonify({
                'success': False,
                'error': 'Plant not found'
            }), 404
        
        data = request.get_json()
        
        if 'name' in data:
            plant.name = data['name'].strip()
        if 'species' in data:
            plant.species = data['species'].strip() if data['species'] else None
        if 'location' in data:
            plant.location = data['location'].strip() if data['location'] else None
        if 'notes' in data:
            plant.notes = data['notes'].strip() if data['notes'] else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'plant': plant.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants/<int:plant_id>', methods=['DELETE'])
@login_required
def delete_plant(plant_id):
    """
    Delete a plant.
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        plant = Plant.query.filter_by(id=plant_id, user_id=g.user_id).first()
        
        if not plant:
            return jsonify({
                'success': False,
                'error': 'Plant not found'
            }), 404
        
        # Delete associated treatments and their reminders
        from models.database_models import Treatment, PlantAnalysis, Notification
        
        # Delete reminders for treatments linked to this plant
        treatment_ids = [t.id for t in Treatment.query.filter_by(plant_id=plant_id, user_id=g.user_id).all()]
        if treatment_ids:
            Reminder.query.filter(Reminder.treatment_id.in_(treatment_ids)).delete(synchronize_session='fetch')
        
        # Delete treatments
        Treatment.query.filter_by(plant_id=plant_id, user_id=g.user_id).delete()
        
        # Delete associated notifications
        Notification.query.filter_by(plant_id=plant_id, user_id=g.user_id).delete()
        
        # Delete associated analyses
        PlantAnalysis.query.filter_by(plant_id=plant_id).delete()
        
        # Delete associated reminders
        Reminder.query.filter_by(plant_id=plant_id).delete()
        
        # Delete image file if exists
        if plant.image_filename:
            try:
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                filename = plant.image_filename.replace('/uploads/', '')
                filepath = os.path.join(upload_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass  # Ignore file deletion errors
        
        db.session.delete(plant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Plant deleted'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants/<int:plant_id>/water', methods=['POST'])
@login_required
def record_watering(plant_id):
    """
    Record watering for a plant.
    
    Response:
        success (bool): Operation success
        plant (dict): Updated plant
    """
    try:
        plant = Plant.query.filter_by(id=plant_id, user_id=g.user_id).first()
        
        if not plant:
            return jsonify({
                'success': False,
                'error': 'Plant not found'
            }), 404
        
        from datetime import datetime
        plant.last_watered = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'plant': plant.to_dict(),
            'message': 'Watering recorded'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants/<int:plant_id>/fertilize', methods=['POST'])
@login_required
def record_fertilizing(plant_id):
    """
    Record fertilizing for a plant.
    
    Response:
        success (bool): Operation success
        plant (dict): Updated plant
    """
    try:
        plant = Plant.query.filter_by(id=plant_id, user_id=g.user_id).first()
        
        if not plant:
            return jsonify({
                'success': False,
                'error': 'Plant not found'
            }), 404
        
        from datetime import datetime
        plant.last_fertilized = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'plant': plant.to_dict(),
            'message': 'Fertilizing recorded'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants/species-care/<species>', methods=['GET'])
def get_species_care(species):
    """
    Get care schedule for a plant species.
    
    Response:
        success (bool): Operation success
        care_schedule (dict): Care schedule for the species
    """
    try:
        care = get_care_schedule_for_species(species)
        
        return jsonify({
            'success': True,
            'species': species,
            'care_schedule': care
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@plant_routes.route('/plants/species-list', methods=['GET'])
def get_species_list():
    """
    Get list of known plant species with care types.
    
    Response:
        success (bool): Operation success
        species (dict): Species to care type mapping
        care_types (list): Available care types
    """
    try:
        defaults = get_care_defaults()
        
        return jsonify({
            'success': True,
            'species': defaults.get('species_mapping', {}),
            'care_types': list(defaults.get('care_defaults', {}).keys())
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
