"""
Notification service for alerts and reminders.
Supports in-app notifications, browser push notifications, and email.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app

from services.translation_service import get_text


class NotificationService:
    """Service for managing notifications and reminders."""
    
    def __init__(self):
        self._db = None
        self._Notification = None
        self._Reminder = None
        self._User = None
        self._Plant = None
        self._mail = None
    
    def set_db(self, db):
        """Set database instance."""
        self._db = db
    
    def set_mail(self, mail):
        """Set Flask-Mail instance."""
        self._mail = mail
    
    @property
    def Notification(self):
        """Lazy load Notification model."""
        if self._Notification is None:
            from models.database_models import Notification
            self._Notification = Notification
        return self._Notification
    
    @property
    def Reminder(self):
        """Lazy load Reminder model."""
        if self._Reminder is None:
            from models.database_models import Reminder
            self._Reminder = Reminder
        return self._Reminder
    
    @property
    def User(self):
        """Lazy load User model."""
        if self._User is None:
            from models.database_models import User
            self._User = User
        return self._User
    
    @property
    def Plant(self):
        """Lazy load Plant model."""
        if self._Plant is None:
            from models.database_models import Plant
            self._Plant = Plant
        return self._Plant
    
    # =========================================================================
    # Notifications
    # =========================================================================
    
    def create_notification(self, user_id: int, type: str, title: str, 
                           message: str = None, plant_id: int = None) -> Optional[Dict]:
        """
        Create a new notification.
        
        Args:
            user_id: User ID
            type: Notification type (water, fertilize, disease_alert, tip, system)
            title: Notification title
            message: Notification message
            plant_id: Optional related plant ID
        
        Returns:
            Created notification dictionary
        """
        try:
            notification = self.Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                plant_id=plant_id
            )
            self._db.session.add(notification)
            self._db.session.commit()
            
            # Try to send push notification
            self._send_push_notification(user_id, title, message)
            
            return notification.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {e}")
            self._db.session.rollback()
            return None
    
    def get_notifications(self, user_id: int, unread_only: bool = False, 
                         limit: int = 50) -> List[Dict]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum notifications to return
        
        Returns:
            List of notification dictionaries
        """
        try:
            query = self.Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(read=False)
            
            notifications = query.order_by(
                self.Notification.created_at.desc()
            ).limit(limit).all()
            
            return [n.to_dict() for n in notifications]
        except Exception as e:
            current_app.logger.error(f"Error getting notifications: {e}")
            return []
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications."""
        try:
            return self.Notification.query.filter_by(
                user_id=user_id, 
                read=False
            ).count()
        except:
            return 0
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        try:
            notification = self.Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                notification.read = True
                self._db.session.commit()
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error marking notification as read: {e}")
            self._db.session.rollback()
            return False
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user."""
        try:
            self.Notification.query.filter_by(
                user_id=user_id,
                read=False
            ).update({'read': True})
            self._db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error marking all notifications as read: {e}")
            self._db.session.rollback()
            return False
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        try:
            notification = self.Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                self._db.session.delete(notification)
                self._db.session.commit()
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error deleting notification: {e}")
            self._db.session.rollback()
            return False
    
    # =========================================================================
    # Reminders
    # =========================================================================
    
    def create_reminder(self, user_id: int, type: str, frequency_days: int,
                       plant_id: int = None, title: str = None) -> Optional[Dict]:
        """
        Create a new reminder.
        
        Args:
            user_id: User ID
            type: Reminder type (water, fertilize, prune, repot, custom)
            frequency_days: Days between reminders
            plant_id: Optional related plant ID
            title: Optional custom title
        
        Returns:
            Created reminder dictionary
        """
        try:
            next_due = datetime.utcnow() + timedelta(days=frequency_days)
            
            reminder = self.Reminder(
                user_id=user_id,
                plant_id=plant_id,
                type=type,
                title=title,
                frequency_days=frequency_days,
                next_due=next_due
            )
            self._db.session.add(reminder)
            self._db.session.commit()
            
            return reminder.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error creating reminder: {e}")
            self._db.session.rollback()
            return None
    
    def get_reminders(self, user_id: int, plant_id: int = None) -> List[Dict]:
        """
        Get reminders for a user.
        
        Args:
            user_id: User ID
            plant_id: Optional filter by plant ID
        
        Returns:
            List of reminder dictionaries
        """
        try:
            query = self.Reminder.query.filter_by(user_id=user_id)
            
            if plant_id:
                query = query.filter_by(plant_id=plant_id)
            
            reminders = query.order_by(self.Reminder.next_due.asc()).all()
            return [r.to_dict() for r in reminders]
        except Exception as e:
            current_app.logger.error(f"Error getting reminders: {e}")
            return []
    
    def get_due_reminders(self, user_id: int) -> List[Dict]:
        """Get reminders that are due or overdue."""
        try:
            now = datetime.utcnow()
            reminders = self.Reminder.query.filter(
                self.Reminder.user_id == user_id,
                self.Reminder.enabled == True,
                self.Reminder.next_due <= now
            ).all()
            return [r.to_dict() for r in reminders]
        except Exception as e:
            current_app.logger.error(f"Error getting due reminders: {e}")
            return []
    
    def get_upcoming_reminders(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get reminders due in the next N days."""
        try:
            now = datetime.utcnow()
            future = now + timedelta(days=days)
            
            reminders = self.Reminder.query.filter(
                self.Reminder.user_id == user_id,
                self.Reminder.enabled == True,
                self.Reminder.next_due <= future
            ).order_by(self.Reminder.next_due.asc()).all()
            
            return [r.to_dict() for r in reminders]
        except Exception as e:
            current_app.logger.error(f"Error getting upcoming reminders: {e}")
            return []
    
    def update_reminder(self, reminder_id: int, user_id: int, 
                       updates: Dict) -> Optional[Dict]:
        """Update a reminder."""
        try:
            reminder = self.Reminder.query.filter_by(
                id=reminder_id,
                user_id=user_id
            ).first()
            
            if not reminder:
                return None
            
            if 'frequency_days' in updates:
                reminder.frequency_days = updates['frequency_days']
            if 'enabled' in updates:
                reminder.enabled = updates['enabled']
            if 'title' in updates:
                reminder.title = updates['title']
            if 'next_due' in updates:
                reminder.next_due = updates['next_due']
            
            self._db.session.commit()
            return reminder.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error updating reminder: {e}")
            self._db.session.rollback()
            return None
    
    def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """Delete a reminder."""
        try:
            reminder = self.Reminder.query.filter_by(
                id=reminder_id,
                user_id=user_id
            ).first()
            
            if reminder:
                self._db.session.delete(reminder)
                self._db.session.commit()
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error deleting reminder: {e}")
            self._db.session.rollback()
            return False
    
    def complete_reminder(self, reminder_id: int, user_id: int) -> Optional[Dict]:
        """
        Mark a reminder as completed and schedule next occurrence.
        """
        try:
            reminder = self.Reminder.query.filter_by(
                id=reminder_id,
                user_id=user_id
            ).first()
            
            if not reminder:
                return None
            
            # Schedule next occurrence
            reminder.next_due = datetime.utcnow() + timedelta(days=reminder.frequency_days)
            self._db.session.commit()
            
            return reminder.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error completing reminder: {e}")
            self._db.session.rollback()
            return None
    
    # =========================================================================
    # Push Notifications
    # =========================================================================
    
    def save_push_subscription(self, user_id: int, subscription: Dict) -> bool:
        """Save push notification subscription for a user."""
        try:
            user = self.User.query.get(user_id)
            if user:
                user.push_subscription = json.dumps(subscription)
                self._db.session.commit()
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error saving push subscription: {e}")
            self._db.session.rollback()
            return False
    
    def _send_push_notification(self, user_id: int, title: str, body: str) -> bool:
        """Send push notification to a user."""
        try:
            user = self.User.query.get(user_id)
            
            if not user or not user.push_subscription or not user.notification_push:
                return False
            
            subscription = json.loads(user.push_subscription)
            
            # Get VAPID keys
            vapid_private = os.getenv('VAPID_PRIVATE_KEY')
            vapid_public = os.getenv('VAPID_PUBLIC_KEY')
            vapid_email = os.getenv('VAPID_CLAIMS_EMAIL', 'mailto:admin@plantcare.local')
            
            if not vapid_private or not vapid_public:
                return False
            
            try:
                from pywebpush import webpush
                
                webpush(
                    subscription_info=subscription,
                    data=json.dumps({
                        'title': title,
                        'body': body,
                        'icon': '/assets/icon.png'
                    }),
                    vapid_private_key=vapid_private,
                    vapid_claims={'sub': vapid_email}
                )
                return True
            except ImportError:
                current_app.logger.warning("pywebpush not available")
                return False
            except Exception as e:
                current_app.logger.error(f"Push notification failed: {e}")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Error sending push notification: {e}")
            return False
    
    # =========================================================================
    # Email Notifications
    # =========================================================================
    
    def send_email_notification(self, user_id: int, subject: str, body: str) -> bool:
        """Send email notification to a user."""
        try:
            if not self._mail:
                return False
            
            user = self.User.query.get(user_id)
            
            if not user or not user.notification_email or user.is_guest:
                return False
            
            from flask_mail import Message
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )
            
            self._mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending email: {e}")
            return False
    
    # =========================================================================
    # Scheduler Tasks
    # =========================================================================
    
    def check_and_trigger_reminders(self):
        """
        Check all due reminders and create notifications.
        Called by background scheduler.
        """
        try:
            now = datetime.utcnow()
            
            # Get all enabled, due reminders
            due_reminders = self.Reminder.query.filter(
                self.Reminder.enabled == True,
                self.Reminder.next_due <= now
            ).all()
            
            for reminder in due_reminders:
                # Get user's language
                user = self.User.query.get(reminder.user_id)
                lang = user.language if user else 'en'
                
                # Get plant name if applicable
                plant_name = ""
                if reminder.plant_id:
                    plant = self.Plant.query.get(reminder.plant_id)
                    if plant:
                        plant_name = plant.name
                
                # Build notification title and message
                type_key = f"{reminder.type}_reminder"
                title = reminder.title or get_text(type_key, lang)
                
                if plant_name:
                    title = f"{title} - {plant_name}"
                
                message = get_text(type_key, lang)
                
                # Create notification
                self.create_notification(
                    user_id=reminder.user_id,
                    type=reminder.type,
                    title=title,
                    message=message,
                    plant_id=reminder.plant_id
                )
                
                # Send email if enabled
                if user and user.notification_email:
                    self.send_email_notification(
                        user_id=reminder.user_id,
                        subject=title,
                        body=message
                    )
                
                # Update next due
                reminder.next_due = now + timedelta(days=reminder.frequency_days)
                self._db.session.commit()
            
            current_app.logger.info(f"Processed {len(due_reminders)} due reminders")
            
        except Exception as e:
            current_app.logger.error(f"Error in reminder check: {e}")
            self._db.session.rollback()


# Global notification service instance
notification_service = NotificationService()


def init_notification_service(db, mail=None):
    """Initialize notification service with database and mail."""
    notification_service.set_db(db)
    if mail:
        notification_service.set_mail(mail)
    return notification_service
