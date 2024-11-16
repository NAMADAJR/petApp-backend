from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '23cb07703407'
down_revision = '0669fdc64711'
branch_labels = None
depends_on = None

def upgrade():
    # Step 1: Create new tables with updated column types and schema changes

    op.create_table('user_pet',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['pet_id'], ['pet.id'], name=op.f('fk_user_pet_pet_id_pet')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_pet_user_id_user')),
        sa.PrimaryKeyConstraint('user_id', 'pet_id')
    )

    # Step 2: Add new columns to activity_record
    op.add_column('activity_record', sa.Column('activity', sa.String(length=100), nullable=False))
    op.add_column('activity_record', sa.Column('duration', sa.Float(), nullable=False))
    op.add_column('activity_record', sa.Column('intensity', sa.String(length=20), nullable=False))

    # Step 3: Create new activity_record table with the updated schema (for SQLite compatibility)
    op.create_table('activity_record_new',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('activity', sa.String(length=100), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('intensity', sa.String(length=20), nullable=False),
    )
    
    # Step 4: Migrate data from old table to the new one (for activity_record)
    op.execute("""
    INSERT INTO activity_record_new (id, pet_id, activity, duration, intensity)
    SELECT id, pet_id, activity, duration, intensity FROM activity_record
    """)

    # Step 5: Create new appointment table (similar steps for other tables)
    op.create_table('appointment_new',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('pet_id', sa.Integer(), nullable=False),
    )
    
    # Migrate data from the old appointment table to the new one
    op.execute("""
    INSERT INTO appointment_new (id, pet_id)
    SELECT id, pet_id FROM appointment
    """)

    # Step 6: Drop old tables (activity_record and appointment)
    op.drop_table('activity_record')
    op.drop_table('appointment')

    # Step 7: Rename new tables to original table names
    op.rename_table('activity_record_new', 'activity_record')
    op.rename_table('appointment_new', 'appointment')

    # Repeat similar steps for other tables such as `pet`, `health_record`, `weight_record`, etc.
    # You can create the new tables for each and migrate data from old to new.

def downgrade():
    # Reverse the upgrade steps: revert the changes back to the old schema

    # Recreate the old `activity_record` and `appointment` tables with their original structure
    op.create_table('activity_record_old',
        sa.Column('id', sa.VARCHAR(length=36), primary_key=True),
        sa.Column('pet_id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
    )
    
    # Migrate data back to the old table
    op.execute("""
    INSERT INTO activity_record_old (id, pet_id, value, unit, type)
    SELECT id, pet_id, value, unit, type FROM activity_record
    """)

    # Drop new table and rename old table back
    op.drop_table('activity_record')
    op.rename_table('activity_record_old', 'activity_record')

    # Reverse the changes for the `appointment` table
    op.create_table('appointment_old',
        sa.Column('id', sa.VARCHAR(length=36), primary_key=True),
        sa.Column('pet_id', sa.VARCHAR(length=36), nullable=False),
    )
    
    op.execute("""
    INSERT INTO appointment_old (id, pet_id)
    SELECT id, pet_id FROM appointment
    """)

    # Drop the new table and rename back to the old name
    op.drop_table('appointment')
    op.rename_table('appointment_old', 'appointment')

    # Continue to reverse changes for other tables (e.g., `pet`, `user`, `health_record`, etc.)
