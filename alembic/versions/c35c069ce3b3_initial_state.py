"""Initial state

Revision ID: c35c069ce3b3
Revises: 
Create Date: 2024-06-02 17:54:30.623767

"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c35c069ce3b3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def read_sql_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

def execute_sql_files_from_folder(folder_path):
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.sql'):
            filepath = os.path.join(folder_path, filename)
            sql_query = read_sql_file(filepath)
            op.execute(sql_query)

def upgrade() -> None:
    execute_sql_files_from_folder(
        os.path.join(os.path.dirname(__file__), '../../migration'))


def downgrade() -> None:
    pass
