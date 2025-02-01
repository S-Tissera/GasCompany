from flask import Blueprint, jsonify, request
from models.delivery_schedule import DeliverySchedule
from models.outlet import Outlet  # Ensure you have an Outlet model
from models.gas_request import GasRequest  # Ensure you have a GasRequest model
from app import db
from sqlalchemy import func, and_
from models.user import User
from utils.notification_service import notify_consumer

dispatch_staff_bp = Blueprint('dispatch_staff', __name__)

# Schedule a gas delivery to an outlet, preventing duplicate schedules for the same delivery date
@dispatch_staff_bp.route('/schedule_delivery', methods=['POST'])
def schedule_delivery():
    data = request.get_json()

    outlet_id = data.get('outletID')
    dispatch_date = data.get('dispatchDate')
    delivery_date = data.get('deliveryDate')
    status = data.get('status', 'Scheduled')

    if not outlet_id or not dispatch_date or not delivery_date:
        return jsonify({"message": "Missing required fields."}), 400

    # Check if the outlet exists
    outlet = Outlet.query.get(outlet_id)
    if not outlet:
        return jsonify({"message": "Invalid outlet ID."}), 404

    # Check if a schedule already exists for this outlet on the same delivery date
    existing_schedule = DeliverySchedule.query.filter(
        and_(
            DeliverySchedule.outletID == outlet_id,
            DeliverySchedule.deliveryDate == delivery_date  # Ensure no duplicate deliveries on the same day
        )
    ).first()

    if existing_schedule:
        return jsonify({
            "message": "A delivery schedule already exists for this outlet on the given delivery date.",
            "scheduleID": existing_schedule.scheduleID,
            "outletID": existing_schedule.outletID,
            "dispatchDate": existing_schedule.dispatchDate,
            "deliveryDate": existing_schedule.deliveryDate,
            "status": existing_schedule.status
        }), 409  # HTTP 409 Conflict

    # Create a new delivery schedule
    new_schedule = DeliverySchedule(
        outletID=outlet_id,
        dispatchDate=dispatch_date,
        deliveryDate=delivery_date,
        status=status
    )

    db.session.add(new_schedule)
    db.session.commit()

    return jsonify({
        "message": "Delivery scheduled successfully.",
        "scheduleID": new_schedule.scheduleID,
        "outletID": new_schedule.outletID,
        "dispatchDate": new_schedule.dispatchDate,
        "deliveryDate": new_schedule.deliveryDate,
        "status": new_schedule.status
    }), 201

# Retrieve a list of all outlets
@dispatch_staff_bp.route('/outlets', methods=['GET'])
def get_outlets():
    outlets = Outlet.query.all()

    if not outlets:
        return jsonify({"message": "No outlets found."}), 404

    outlet_data = [
        {
            "outletID": outlet.outletID,
            "name": outlet.name,
            "location": outlet.location,
        }
        for outlet in outlets
    ]

    return jsonify({"outlets": outlet_data}), 200

# Retrieve all gas requests grouped by day, including counts of Pending and Scheduled requests
@dispatch_staff_bp.route('/requests_by_day', methods=['GET'])
def get_requests_by_day():
    requests = (
        db.session.query(
            func.date(GasRequest.requestedDate).label("date"),
            GasRequest.requestID,
            GasRequest.userID,
            GasRequest.outletID,
            GasRequest.status,
            GasRequest.pickupPeriodStart,
            GasRequest.pickupPeriodEnd,
        )
        .order_by(func.date(GasRequest.requestedDate))
        .all()
    )

    if not requests:
        return jsonify({"message": "No gas requests found."}), 404

    requests_by_day = {}

    for request in requests:
        date = request.date.strftime("%Y-%m-%d")

        if date not in requests_by_day:
            requests_by_day[date] = {
                "Pending_Requests": [],
                "Scheduled_Requests": [],
                "Pending_Count": 0,
                "Scheduled_Count": 0
            }

        request_data = {
            "requestID": request.requestID,
            "userID": request.userID,
            "outletID": request.outletID,
            "status": request.status,
            "pickupPeriodStart": request.pickupPeriodStart,
            "pickupPeriodEnd": request.pickupPeriodEnd
        }

        if request.status == "Pending":
            requests_by_day[date]["Pending_Requests"].append(request_data)
            requests_by_day[date]["Pending_Count"] += 1
        elif request.status == "Scheduled":
            requests_by_day[date]["Scheduled_Requests"].append(request_data)
            requests_by_day[date]["Scheduled_Count"] += 1

    return jsonify({"requests_by_day": requests_by_day}), 200

# Update a scheduled delivery and notify affected users
@dispatch_staff_bp.route('/update_delivery/<int:schedule_id>', methods=['PUT'])
def update_scheduled_delivery(schedule_id):
    data = request.get_json()  # Now 'request' is properly imported

    new_dispatch_date = data.get('dispatchDate')
    new_delivery_date = data.get('deliveryDate')
    new_status = data.get('status')

    # Find the schedule by ID
    delivery_schedule = DeliverySchedule.query.get(schedule_id)
    if not delivery_schedule:
        return jsonify({"message": "Delivery schedule not found."}), 404

    # Prevent duplicate schedules for the same outlet & delivery date
    if new_delivery_date and new_delivery_date != delivery_schedule.deliveryDate:
        existing_schedule = DeliverySchedule.query.filter(
            and_(
                DeliverySchedule.outletID == delivery_schedule.outletID,
                DeliverySchedule.deliveryDate == new_delivery_date
            )
        ).first()
        if existing_schedule:
            return jsonify({
                "message": "A delivery schedule already exists for this outlet on the given delivery date.",
                "existingScheduleID": existing_schedule.scheduleID
            }), 409  # HTTP 409 Conflict

    # Update fields if provided
    if new_dispatch_date:
        delivery_schedule.dispatchDate = new_dispatch_date
    if new_delivery_date:
        delivery_schedule.deliveryDate = new_delivery_date
    if new_status:
        delivery_schedule.status = new_status

    db.session.commit()

    # Find all users with gas requests at this outlet
    affected_requests = GasRequest.query.filter(
        and_(
            GasRequest.outletID == delivery_schedule.outletID,
            GasRequest.status.in_(["Pending", "Scheduled"])  # Notify only pending & scheduled requests
        )
    ).all()

    # Notify affected users
    for request in affected_requests:
        user = User.query.get(request.userID)
        if user:
            message = f"Your gas request (ID: {request.requestID}) is affected by an updated delivery schedule. New delivery date: {delivery_schedule.deliveryDate}."
            notify_consumer(user.userID, message)

    return jsonify({
        "message": "Delivery schedule updated successfully.",
        "scheduleID": delivery_schedule.scheduleID,
        "outletID": delivery_schedule.outletID,
        "dispatchDate": delivery_schedule.dispatchDate,
        "deliveryDate": delivery_schedule.deliveryDate,
        "status": delivery_schedule.status,
        "notifiedUsers": len(affected_requests)
    }), 200
