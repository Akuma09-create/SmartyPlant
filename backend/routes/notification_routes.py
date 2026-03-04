"""
Notification and reminder routes.
"""

from flask import Blueprint, request, jsonify, g
from auth import login_required
from services.notification_service import notification_service

# Create blueprint
notification_routes = Blueprint('notifications', __name__, url_prefix='/api/v1')


# =============================================================================
# Notification Routes
# =============================================================================

@notification_routes.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """
    Get notifications for current user.
    
    Query params:
        unread_only (bool, optional): Only return unread notifications
        limit (int, optional): Maximum notifications to return (default 50)
    
    Response:
        success (bool): Operation success
        notifications (list): List of notifications
        unread_count (int): Number of unread notifications
    """
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)
        
        notifications = notification_service.get_notifications(
            g.user_id, unread_only, limit
        )
        unread_count = notification_service.get_unread_count(g.user_id)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/notifications/count', methods=['GET'])
@login_required
def get_notification_count():
    """
    Get unread notification count.
    
    Response:
        success (bool): Operation success
        count (int): Unread count
    """
    try:
        count = notification_service.get_unread_count(g.user_id)
        
        return jsonify({
            'success': True,
            'count': count
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """
    Mark a notification as read.
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        success = notification_service.mark_as_read(notification_id, g.user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """
    Mark all notifications as read.
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        success = notification_service.mark_all_as_read(g.user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'All notifications marked as read'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to mark notifications as read'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """
    Delete a notification.
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        success = notification_service.delete_notification(notification_id, g.user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification deleted'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/notifications/subscribe', methods=['POST'])
@login_required
def subscribe_push():
    """
    Register push notification subscription.
    
    Request JSON:
        subscription (object): Web Push subscription object
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        data = request.get_json()
        
        if not data or 'subscription' not in data:
            return jsonify({
                'success': False,
                'error': 'Subscription object is required'
            }), 400
        
        success = notification_service.save_push_subscription(
            g.user_id, 
            data['subscription']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Push subscription saved'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save subscription'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


# =============================================================================
# Reminder Routes
# =============================================================================

@notification_routes.route('/reminders', methods=['GET'])
@login_required
def get_reminders():
    """
    Get reminders for current user.
    
    Query params:
        plant_id (int, optional): Filter by plant ID
    
    Response:
        success (bool): Operation success
        reminders (list): List of reminders
    """
    try:
        plant_id = request.args.get('plant_id', type=int)
        reminders = notification_service.get_reminders(g.user_id, plant_id)
        
        return jsonify({
            'success': True,
            'reminders': reminders
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/reminders/upcoming', methods=['GET'])
@login_required
def get_upcoming_reminders():
    """
    Get upcoming reminders (next 7 days by default).
    
    Query params:
        days (int, optional): Number of days to look ahead (default 7)
    
    Response:
        success (bool): Operation success
        reminders (list): List of upcoming reminders
    """
    try:
        days = request.args.get('days', 7, type=int)
        days = min(days, 30)
        
        reminders = notification_service.get_upcoming_reminders(g.user_id, days)
        
        return jsonify({
            'success': True,
            'reminders': reminders
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/reminders', methods=['POST'])
@login_required
def create_reminder():
    """
    Create a new reminder.
    
    Request JSON:
        type (str): Reminder type (water, fertilize, prune, repot, custom)
        frequency_days (int): Days between reminders
        plant_id (int, optional): Related plant ID
        title (str, optional): Custom title
    
    Response:
        success (bool): Operation success
        reminder (dict): Created reminder
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        reminder_type = data.get('type', '').strip()
        frequency_days = data.get('frequency_days', 0)
        
        if not reminder_type:
            return jsonify({
                'success': False,
                'error': 'Reminder type is required'
            }), 400
        
        if not frequency_days or frequency_days < 1:
            return jsonify({
                'success': False,
                'error': 'Valid frequency_days is required'
            }), 400
        
        reminder = notification_service.create_reminder(
            user_id=g.user_id,
            type=reminder_type,
            frequency_days=frequency_days,
            plant_id=data.get('plant_id'),
            title=data.get('title')
        )
        
        if reminder:
            return jsonify({
                'success': True,
                'reminder': reminder
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create reminder'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/reminders/<int:reminder_id>', methods=['PUT'])
@login_required
def update_reminder(reminder_id):
    """
    Update a reminder.
    
    Request JSON:
        frequency_days (int, optional): Days between reminders
        enabled (bool, optional): Whether reminder is enabled
        title (str, optional): Custom title
    
    Response:
        success (bool): Operation success
        reminder (dict): Updated reminder
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        reminder = notification_service.update_reminder(
            reminder_id, g.user_id, data
        )
        
        if reminder:
            return jsonify({
                'success': True,
                'reminder': reminder
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Reminder not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/reminders/<int:reminder_id>', methods=['DELETE'])
@login_required
def delete_reminder(reminder_id):
    """
    Delete a reminder.
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        success = notification_service.delete_reminder(reminder_id, g.user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Reminder deleted'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Reminder not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@notification_routes.route('/reminders/<int:reminder_id>/complete', methods=['POST'])
@login_required
def complete_reminder(reminder_id):
    """
    Mark a reminder as completed (schedules next occurrence).
    
    Response:
        success (bool): Operation success
        reminder (dict): Updated reminder with new next_due
    """
    try:
        reminder = notification_service.complete_reminder(reminder_id, g.user_id)
        
        if reminder:
            return jsonify({
                'success': True,
                'reminder': reminder,
                'message': 'Reminder completed, next occurrence scheduled'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Reminder not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
