"""populate users

Revision ID: 5bc48631688c
Revises: 000602394677
Create Date: 2025-07-02 17:33:01.567141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bc48631688c'
down_revision: Union[str, None] = '000602394677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    users = [
        {"email": "user1@example.com", "hashed_password": "$2b$12$abc", "first_name": "John", "last_name": "Doe", "phone_number": "9876543210", "user_type": "supplier", "is_active": True, "is_deleted": False},
        {"email": "user2@example.com", "hashed_password": "$2b$12$def", "first_name": "Jane", "last_name": "Smith", "phone_number": "9876543211", "user_type": "importer_exporter", "is_active": True, "is_deleted": False},
        {"email": "user3@example.com", "hashed_password": "$2b$12$ghi", "first_name": "Bob", "last_name": "Brown", "phone_number": "9876543212", "user_type": "super_admin", "is_active": True, "is_deleted": False},
        # add 17 more users below with varied types
        {"email": "user4@example.com", "hashed_password": "$2b$12$jkl", "first_name": "Alice", "last_name": "Wonder", "phone_number": "9876543213", "user_type": "supplier", "is_active": True, "is_deleted": False},
        {"email": "user5@example.com", "hashed_password": "$2b$12$mno", "first_name": "Charlie", "last_name": "Stone", "phone_number": "9876543214", "user_type": "importer_exporter", "is_active": True, "is_deleted": False},
        {"email": "user6@example.com", "hashed_password": "$2b$12$pqr", "first_name": "Eva", "last_name": "Green", "phone_number": "9876543215", "user_type": "super_admin", "is_active": True, "is_deleted": False},
        {"email": "user7@example.com", "hashed_password": "$2b$12$stu", "first_name": "Tom", "last_name": "White", "phone_number": "9876543216", "user_type": "supplier", "is_active": True, "is_deleted": False},
        {"email": "user8@example.com", "hashed_password": "$2b$12$vwx", "first_name": "Lily", "last_name": "Gray", "phone_number": "9876543217", "user_type": "importer_exporter", "is_active": True, "is_deleted": False},
        {"email": "user9@example.com", "hashed_password": "$2b$12$yz1", "first_name": "Harry", "last_name": "Potter", "phone_number": "9876543218", "user_type": "super_admin", "is_active": True, "is_deleted": False},
        {"email": "user10@example.com", "hashed_password": "$2b$12$234", "first_name": "Ron", "last_name": "Weasley", "phone_number": "9876543219", "user_type": "supplier", "is_active": True, "is_deleted": False},
        {"email": "user11@example.com", "hashed_password": "$2b$12$567", "first_name": "Hermione", "last_name": "Granger", "phone_number": "9876543220", "user_type": "importer_exporter", "is_active": True, "is_deleted": False},
        {"email": "user12@example.com", "hashed_password": "$2b$12$890", "first_name": "Draco", "last_name": "Malfoy", "phone_number": "9876543221", "user_type": "super_admin", "is_active": True, "is_deleted": False},
        {"email": "user13@example.com", "hashed_password": "$2b$12$abc", "first_name": "Ginny", "last_name": "Weasley", "phone_number": "9876543222", "user_type": "supplier", "is_active": True, "is_deleted": False},
        {"email": "user14@example.com", "hashed_password": "$2b$12$def", "first_name": "Fred", "last_name": "Weasley", "phone_number": "9876543223", "user_type": "importer_exporter", "is_active": True, "is_deleted": False},
        {"email": "user15@example.com", "hashed_password": "$2b$12$ghi", "first_name": "George", "last_name": "Weasley", "phone_number": "9876543224", "user_type": "super_admin", "is_active": True, "is_deleted": False},
        {"email": "user16@example.com", "hashed_password": "$2b$12$jkl", "first_name": "Neville", "last_name": "Longbottom", "phone_number": "9876543225", "user_type": "supplier", "is_active": True, "is_deleted": False},
        {"email": "user17@example.com", "hashed_password": "$2b$12$mno", "first_name": "Luna", "last_name": "Lovegood", "phone_number": "9876543226", "user_type": "importer_exporter", "is_active": True, "is_deleted": False},
        {"email": "user18@example.com", "hashed_password": "$2b$12$pqr", "first_name": "Cho", "last_name": "Chang", "phone_number": "9876543227", "user_type": "super_admin", "is_active": True, "is_deleted": False},
        {"email": "user19@example.com", "hashed_password": "$2b$12$stu", "first_name": "Cedric", "last_name": "Diggory", "phone_number": "9876543228", "user_type": "supplier", "is_active": True, "is_deleted": False},
        {"email": "user20@example.com", "hashed_password": "$2b$12$vwx", "first_name": "Sirius", "last_name": "Black", "phone_number": "9876543229", "user_type": "importer_exporter", "is_active": True, "is_deleted": False},
    ]

    conn = op.get_bind()
    for user in users:
        conn.execute(
            sa.text("""
                INSERT INTO users 
                (email, hashed_password, first_name, last_name, phone_number, user_type, is_active, created_at, updated_at, is_deleted)
                VALUES 
                (:email, :hashed_password, :first_name, :last_name, :phone_number, :user_type, :is_active, now(), now(), :is_deleted)
            """), user
        )


def downgrade():
    conn = op.get_bind()
    emails = [
        "user1@example.com", "user2@example.com", "user3@example.com", "user4@example.com", "user5@example.com",
        "user6@example.com", "user7@example.com", "user8@example.com", "user9@example.com", "user10@example.com",
        "user11@example.com", "user12@example.com", "user13@example.com", "user14@example.com", "user15@example.com",
        "user16@example.com", "user17@example.com", "user18@example.com", "user19@example.com", "user20@example.com"
    ]
    conn.execute(
        sa.text("DELETE FROM users WHERE email = ANY(:emails)")
        .bindparams(sa.bindparam('emails', expanding=True)),
        {"emails": emails}
    )