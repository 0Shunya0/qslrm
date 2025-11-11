"""
Database Triggers Monitoring Routes
Real-time trigger statistics and management
"""

from flask import Blueprint, jsonify, request
from models import db, AccessLog, Researcher
from sqlalchemy import text, func
from datetime import datetime, timedelta

triggers_bp = Blueprint('triggers', __name__)

@triggers_bp.route('/status', methods=['GET'])
def get_trigger_status():
    """Get all database triggers and their status"""
    try:
        # Query SQLite system tables for trigger information
        query = text("""
            SELECT 
                name,
                tbl_name as table_name,
                sql
            FROM sqlite_master 
            WHERE type = 'trigger'
            ORDER BY tbl_name, name
        """)
        
        result = db.session.execute(query)
        triggers = []
        
        for row in result:
            triggers.append({
                'name': row.name,
                'table': row.table_name,
                'status': 'active',  # SQLite doesn't have disabled triggers
                'definition': row.sql
            })
        
        return jsonify({
            'total_triggers': len(triggers),
            'triggers': triggers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@triggers_bp.route('/activity', methods=['GET'])
def get_trigger_activity():
    """Get trigger activity statistics from access logs"""
    try:
        # Get time range from query params (default: last 24 hours)
        hours = request.args.get('hours', 24, type=int)
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get action counts (proxy for trigger activity)
        activity = db.session.query(
            AccessLog.action_type,
            AccessLog.target_entity,
            func.count(AccessLog.log_id).label('count'),
            func.max(AccessLog.timestamp).label('last_fired')
        ).filter(
            AccessLog.timestamp >= cutoff
        ).group_by(
            AccessLog.action_type,
            AccessLog.target_entity
        ).all()
        
        # Get hourly breakdown for charts
        hourly = db.session.query(
            func.strftime('%H:00', AccessLog.timestamp).label('hour'),
            func.count(AccessLog.log_id).label('executions')
        ).filter(
            AccessLog.timestamp >= cutoff
        ).group_by(
            func.strftime('%H', AccessLog.timestamp)
        ).order_by('hour').all()
        
        hourly_data = [{'time': h.hour, 'executions': h.executions} for h in hourly]
        
        # Format trigger activity
        trigger_stats = []
        for act in activity:
            trigger_name = f"{act.action_type}_{act.target_entity}"
            trigger_stats.append({
                'name': trigger_name,
                'table': act.target_entity,
                'status': 'active',
                'fires': act.count,
                'lastFired': f"{(datetime.utcnow() - act.last_fired).seconds // 60} mins ago" if act.last_fired else 'Never'
            })
        
        return jsonify({
            'trigger_activity': trigger_stats,
            'hourly_breakdown': hourly_data,
            'time_range_hours': hours
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@triggers_bp.route('/recent', methods=['GET'])
def get_recent_trigger_events():
    """Get recent trigger-related events"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Get recent access logs (represents trigger activity)
        logs = AccessLog.query.order_by(
            AccessLog.timestamp.desc()
        ).limit(limit).all()
        
        events = []
        for log in logs:
            researcher = Researcher.query.get(log.researcher_id)
            
            # Determine severity
            if log.action_type in ['create', 'update']:
                severity = 'info'
            elif log.action_type == 'delete':
                severity = 'warning'
            elif log.action_type in ['login', 'logout']:
                severity = 'success'
            else:
                severity = 'info'
            
            # Create message
            message = f"{log.action_type.capitalize()} {log.target_entity}"
            if researcher:
                message += f" by {researcher.first_name} {researcher.last_name}"
            
            time_diff = datetime.utcnow() - log.timestamp
            if time_diff.seconds < 60:
                time_ago = f"{time_diff.seconds} secs ago"
            elif time_diff.seconds < 3600:
                time_ago = f"{time_diff.seconds // 60} mins ago"
            else:
                time_ago = f"{time_diff.seconds // 3600} hours ago"
            
            events.append({
                'type': 'trigger' if log.action_type in ['create', 'update', 'delete'] else 'system',
                'message': message,
                'time': time_ago,
                'severity': severity,
                'timestamp': log.timestamp.isoformat()
            })
        
        return jsonify(events)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@triggers_bp.route('/stats', methods=['GET'])
def get_trigger_statistics():
    """Get overall trigger statistics"""
    try:
        # Total trigger executions (from access logs)
        total_executions = AccessLog.query.count()
        
        # Executions in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_executions = AccessLog.query.filter(
            AccessLog.timestamp >= one_hour_ago
        ).count()
        
        # Most active trigger (most common action)
        most_active = db.session.query(
            AccessLog.action_type,
            AccessLog.target_entity,
            func.count(AccessLog.log_id).label('count')
        ).group_by(
            AccessLog.action_type,
            AccessLog.target_entity
        ).order_by(
            func.count(AccessLog.log_id).desc()
        ).first()
        
        # Get actual database triggers count
        trigger_count_query = text("""
            SELECT COUNT(*) as count
            FROM sqlite_master 
            WHERE type = 'trigger'
        """)
        trigger_count = db.session.execute(trigger_count_query).scalar()
        
        return jsonify({
            'total_database_triggers': trigger_count or 0,
            'total_executions': total_executions,
            'executions_last_hour': recent_executions,
            'most_active_trigger': {
                'name': f"{most_active.action_type}_{most_active.target_entity}" if most_active else None,
                'executions': most_active.count if most_active else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@triggers_bp.route('/create', methods=['POST'])
def create_trigger():
    """Create a new database trigger"""
    try:
        data = request.get_json()
        
        required = ['name', 'table', 'event', 'sql']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Construct trigger SQL
        trigger_sql = f"""
        CREATE TRIGGER {data['name']}
        {data['event']} ON {data['table']}
        BEGIN
            {data['sql']}
        END;
        """
        
        # Execute trigger creation
        db.session.execute(text(trigger_sql))
        db.session.commit()
        
        return jsonify({
            'message': 'Trigger created successfully',
            'trigger_name': data['name']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@triggers_bp.route('/delete/<trigger_name>', methods=['DELETE'])
def delete_trigger(trigger_name):
    """Delete a database trigger"""
    try:
        drop_sql = f"DROP TRIGGER IF EXISTS {trigger_name}"
        db.session.execute(text(drop_sql))
        db.session.commit()
        
        return jsonify({
            'message': f'Trigger {trigger_name} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500