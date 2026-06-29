# dashboard.py
from flask import Blueprint, render_template, request, jsonify, Response, stream_with_context, session
from flask_login import login_required, current_user
from model.models import db, ChatSession, Message, RetrievedChunk
import requests
import time
import json

dashboard = Blueprint('dashboard', __name__)

RAG_API_URL = "http://localhost:8000/query"

@dashboard.route('/')
@login_required
def index():
    session_obj = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).first()
    if not session_obj:
        session_obj = ChatSession(user_id=current_user.id)
        db.session.add(session_obj)
        db.session.commit()

    # Fetch messages and convert to dict
    messages = Message.query.filter_by(session_id=session_obj.id).order_by(Message.created_at).all()
    messages_data = [
        {
            "id": msg.id,
            "session_id": msg.session_id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }
        for msg in messages
    ]

    chunks = RetrievedChunk.query.filter_by(session_id=session_obj.id).all()
    chunk_dicts = []
    for c in chunks:
        try:
            meta = json.loads(c.metadata_json)
        except (json.JSONDecodeError, TypeError):
            meta = {}
        chunk_dicts.append({'page_content': c.page_content, 'metadata': meta})

    return render_template('dashboard/index.html', messages=messages_data, chunks=chunk_dicts)

@dashboard.route('/send_message', methods=['POST'])
@login_required
def send_message():
    user_message = request.json.get('message', '').strip()
    top_k = request.json.get('top_k', 5)

    if not user_message:
        return jsonify({"error": "پیام خالی است"}), 400

    session_obj = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).first()
    if not session_obj:
        session_obj = ChatSession(user_id=current_user.id)
        db.session.add(session_obj)
        db.session.commit()

    user_msg = Message(session_id=session_obj.id, role='user', content=user_message)
    db.session.add(user_msg)
    db.session.commit()

    try:
        response = requests.post("http://localhost:8000/query", json={"message": user_message, "top_k": top_k}, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Backend error: {response.text}")

        result = response.json()
        full_response = result["response"]
        chunks = result.get("chunks", [])

        assistant_msg = Message(session_id=session_obj.id, role='assistant', content=full_response)
        db.session.add(assistant_msg)

        for chunk in chunks:
            meta_json = json.dumps(chunk.get('metadata', {}), ensure_ascii=False)
            rc = RetrievedChunk(
                session_id=session_obj.id,
                page_content=chunk.get('page_content', ''),
                metadata_json=meta_json
            )
            db.session.add(rc)
        db.session.commit()

        return jsonify({
            "content": full_response,
            "chunks": chunks
        })

    except Exception as e:
        error_msg = f"خطا در ارتباط با سرور: {str(e)}"
        err_msg = Message(session_id=session_obj.id, role='assistant', content=error_msg)
        db.session.add(err_msg)
        db.session.commit()
        return jsonify({"content": error_msg, "chunks": []}), 500

@dashboard.route('/clear_chat', methods=['POST'])
@login_required
def clear_chat():
    new_session = ChatSession(user_id=current_user.id)
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"status": "cleared", "new_session_id": new_session.id})