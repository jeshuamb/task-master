from app import db, current_user
from ..utils import get_ve
from datetime import datetime, timezone

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(150), nullable=False)
    datetime_created = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def formatted_datetime(self):
        VE = get_ve()
        if not self.datetime_created:
            return ""

        return self.datetime_created.astimezone(VE).strftime("%d/%m/%Y %H:%M:%S")
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    @staticmethod
    def get_tasks():
        return Task.query.order_by(Task.datetime_created)
    
    @staticmethod
    def get_task_by_id(id):
        return db.session.get(Task, id)