"""add_new_column_to_user

Revision ID: 211e1f1c85f7
Revises: 
Create Date: 2024-02-05 10:17:50.961902

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean
from sqlalchemy.engine.reflection import Inspector
import datetime

# revision identifiers, used by Alembic.
revision = "211e1f1c85f7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    inspector = Inspector.from_engine(op.get_bind())

    # if "month" not in [
    #     column["name"] for column in inspector.get_columns("insolation")
    # ]:
    #     op.add_column("insolation", sa.Column("month", sa.String(50), nullable=True))

    # if "fi" in [column["name"] for column in inspector.get_columns("insolation")]:
    #     op.alter_column("insolation", "fi", type_=sa.String(50), nullable=True)

    # # if "h_coordinate" in [
    # #     column["name"] for column in inspector.get_columns("insolation")
    # # ]:
    # #     op.alter_column("insolation", "h_coordinate", type_=sa.Float, nullable=True)
    
    # if "username" not in [
    #     column["name"] for column in inspector.get_columns("insolation")
    # ]:
    #     op.add_column("insolation", sa.Column("username", sa.String(255), nullable=True))
        
        
    # if "board_id" not in [
    #     column["name"] for column in inspector.get_columns("insolation")
    # ]:
    #     op.add_column("insolation", sa.Column("board_id", sa.Integer, nullable=True))
        
    # if "company_id" not in [
    #     column["name"] for column in inspector.get_columns("insolation")
    # ]:
    #     op.add_column("insolation", sa.Column("company_id", sa.Integer, nullable=True))
     
    # if "company_name" not in [
    #     column["name"] for column in inspector.get_columns("insolation")
    # ]:
    #     op.add_column("insolation", sa.Column("company_name", sa.String(255), nullable=True)) 
        
    # if "board_name" not in [
    #     column["name"] for column in inspector.get_columns("insolation")
    # ]:
    #     op.add_column("insolation", sa.Column("board_name", sa.String(255), nullable=True))  
     
    if "created_by" not in [
        column["name"] for column in inspector.get_columns("courses")
    ]:
        op.add_column("courses", sa.Column("created_by", sa.String(50), nullable=False))  
    
    # op.drop_column('insolation', 'board_id')    
    
    # op.drop_table('attendance_records')
    # op.drop_table('qr_sessions')
    # op.drop_table('instructor_course')
    # op.drop_table('students')
    # op.drop_table('instructors')
    # op.drop_table('courses')
    # op.drop_table('users')

        
def downgrade():

    pass


