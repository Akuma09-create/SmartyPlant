"""Database models for storing plant analysis and history."""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


# ============================================================================
# User & Authentication Models
# ============================================================================

class User(db.Model):
    """User model for authentication and profile."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), default='en')  # en, hi, mr
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_guest = db.Column(db.Boolean, default=False)
    push_subscription = db.Column(db.Text)  # JSON for web push subscription
    notification_email = db.Column(db.Boolean, default=True)
    notification_push = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plants = db.relationship('Plant', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    analyses = db.relationship('PlantAnalysis', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    treatments = db.relationship('Treatment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'language': self.language,
            'email_verified': self.email_verified,
            'is_guest': self.is_guest,
            'notification_email': self.notification_email,
            'notification_push': self.notification_push,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Plant(db.Model):
    """User's plant for tracking and reminders."""
    
    __tablename__ = 'plants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(150))
    location = db.Column(db.String(100))  # indoor, outdoor, garden, balcony
    image_filename = db.Column(db.String(255))
    age_days = db.Column(db.Integer)
    watering_frequency_days = db.Column(db.Integer, default=7)
    fertilizer_frequency_days = db.Column(db.Integer, default=30)
    last_watered = db.Column(db.DateTime)
    last_fertilized = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('PlantAnalysis', backref='plant', lazy='dynamic')
    reminders = db.relationship('Reminder', backref='plant', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Plant {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'species': self.species,
            'location': self.location,
            'image_filename': self.image_filename,
            'age_days': self.age_days,
            'watering_frequency_days': self.watering_frequency_days,
            'fertilizer_frequency_days': self.fertilizer_frequency_days,
            'last_watered': self.last_watered.isoformat() if self.last_watered else None,
            'last_fertilized': self.last_fertilized.isoformat() if self.last_fertilized else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'next_watering': self.next_watering.isoformat() if self.next_watering else None,
            'next_fertilizing': self.next_fertilizing.isoformat() if self.next_fertilizing else None
        }
    
    @property
    def next_watering(self):
        """Calculate next watering date."""
        if self.last_watered and self.watering_frequency_days:
            return self.last_watered + timedelta(days=self.watering_frequency_days)
        return None
    
    @property
    def next_fertilizing(self):
        """Calculate next fertilizing date."""
        if self.last_fertilized and self.fertilizer_frequency_days:
            return self.last_fertilized + timedelta(days=self.fertilizer_frequency_days)
        return None


# ============================================================================
# Notification & Reminder Models
# ============================================================================

class Notification(db.Model):
    """In-app notifications for users."""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)  # water, fertilize, disease_alert, tip, system
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), index=True)
    read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'plant_id': self.plant_id,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Reminder(db.Model):
    """Recurring reminders for plant care."""
    
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), index=True)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), index=True)
    type = db.Column(db.String(50), nullable=False)  # water, fertilize, prune, repot, treatment, custom
    title = db.Column(db.String(200))
    frequency_days = db.Column(db.Integer, nullable=False)
    next_due = db.Column(db.DateTime, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reminder {self.id}: {self.type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'plant_id': self.plant_id,
            'treatment_id': self.treatment_id,
            'type': self.type,
            'title': self.title,
            'frequency_days': self.frequency_days,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================================
# Chat Models
# ============================================================================

class ChatMessage(db.Model):
    """Chat history for AI assistant."""
    
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('plant_analysis.id'), index=True)  # Context reference
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.role}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'analysis_id': self.analysis_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================================
# Analysis Models
# ============================================================================

class PlantAnalysis(db.Model):
    """Model to store individual plant analysis results."""
    
    __tablename__ = 'plant_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), index=True)
    image_filename = db.Column(db.String(255), nullable=False)
    plant_type = db.Column(db.String(100))
    disease_detected = db.Column(db.String(255))
    confidence_score = db.Column(db.Float)
    health_score = db.Column(db.Float)  # Overall health percentage
    severity_level = db.Column(db.String(50))  # mild, moderate, severe
    analysis_details = db.Column(db.Text)  # JSON string with detailed analysis
    recommended_actions = db.Column(db.Text)  # JSON string with care advice
    language = db.Column(db.String(10), default='en')  # Language of analysis
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship for chat messages
    chat_messages = db.relationship('ChatMessage', backref='analysis', lazy='dynamic')
    
    def __repr__(self):
        return f'<PlantAnalysis {self.id}: {self.disease_detected}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        details = self.analysis_details
        actions = self.recommended_actions
        
        # Parse JSON if stored as string
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                pass
        if isinstance(actions, str):
            try:
                actions = json.loads(actions)
            except:
                pass
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plant_id': self.plant_id,
            'image_filename': self.image_filename,
            'plant_type': self.plant_type,
            'disease_detected': self.disease_detected,
            'confidence_score': self.confidence_score,
            'health_score': self.health_score,
            'severity_level': self.severity_level,
            'analysis_details': details,
            'recommended_actions': actions,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AnalysisHistory(db.Model):
    """Model to store history of all analyses for a user/session."""
    
    __tablename__ = 'analysis_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    session_id = db.Column(db.String(255), index=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('plant_analysis.id'), nullable=False)
    plant_location = db.Column(db.String(255))  # e.g., 'garden', 'indoor'
    plant_age_days = db.Column(db.Integer)
    weather_conditions = db.Column(db.String(100))  # e.g., 'sunny', 'rainy'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    analysis = db.relationship('PlantAnalysis', backref='history_entries')
    
    def __repr__(self):
        return f'<AnalysisHistory {self.id}: user {self.user_id}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'analysis_id': self.analysis_id,
            'plant_location': self.plant_location,
            'plant_age_days': self.plant_age_days,
            'weather_conditions': self.weather_conditions,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================================
# Treatment Models
# ============================================================================

class Treatment(db.Model):
    """Model to track plant treatment progress."""
    
    __tablename__ = 'treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), index=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('plant_analysis.id'), index=True)
    
    # Treatment details
    disease_name = db.Column(db.String(255), nullable=False)
    treatment_type = db.Column(db.String(50), nullable=False)  # organic, chemical, cultural
    severity = db.Column(db.String(50))  # mild, moderate, severe
    
    # Treatment steps (JSON array)
    steps = db.Column(db.Text, nullable=False)  # JSON: [{step, description, completed, completed_at}]
    current_step = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=0)
    
    # Progress tracking
    status = db.Column(db.String(50), default='active', index=True)  # active, completed, abandoned
    progress_percent = db.Column(db.Float, default=0.0)
    
    # Timeline
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_duration_days = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime)
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reminders = db.relationship('Reminder', backref='treatment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Treatment {self.id}: {self.disease_name} - {self.status}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        steps_data = self.steps
        if isinstance(steps_data, str):
            try:
                steps_data = json.loads(steps_data)
            except:
                steps_data = []
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plant_id': self.plant_id,
            'analysis_id': self.analysis_id,
            'disease_name': self.disease_name,
            'treatment_type': self.treatment_type,
            'severity': self.severity,
            'steps': steps_data,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'status': self.status,
            'progress_percent': self.progress_percent,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'estimated_duration_days': self.estimated_duration_days,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_progress(self):
        """Recalculate progress based on completed steps."""
        if self.total_steps > 0:
            steps_data = self.steps
            if isinstance(steps_data, str):
                try:
                    steps_data = json.loads(steps_data)
                except:
                    steps_data = []
            
            completed_count = sum(1 for step in steps_data if step.get('completed', False))
            self.progress_percent = (completed_count / self.total_steps) * 100
            self.current_step = completed_count
            
            if completed_count >= self.total_steps:
                self.status = 'completed'
                self.completed_at = datetime.utcnow()

