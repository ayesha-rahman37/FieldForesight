"""initial schema

Revision ID: ce17a4b2f8d1
Revises: 
Create Date: 2026-10-21 14:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ce17a4b2f8d1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # user_sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # crops
    op.create_table(
        'crops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # regions
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # crop_varieties
    op.create_table(
        'crop_varieties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('variety_code', sa.String(length=50), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_bn', sa.String(length=100), nullable=True),
        sa.Column('variety_type', sa.String(length=50), nullable=True),
        sa.Column('yield_coefficient', sa.Numeric(precision=6, scale=4), nullable=False, server_default='1.0'),
        sa.Column('potential_yield_min', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('potential_yield_max', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('maturity_days', sa.Integer(), nullable=True),
        sa.Column('season', sa.String(length=50), nullable=True),
        sa.Column('stress_tolerance', sa.String(length=100), nullable=True),
        sa.Column('description_bn', sa.Text(), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('is_recommended', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('variety_code')
    )

    # historical_yield
    op.create_table(
        'historical_yield',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crop_id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('rainfall', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('temperature', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('yield_value', sa.Numeric(precision=6, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('crop_id', 'region_id', 'year', name='uq_historical_yield_crop_region_year')
    )

    # model_metadata
    op.create_table(
        'model_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('model_path', sa.String(length=500), nullable=False),
        sa.Column('training_records', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mae', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('rmse', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('mape', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('trained_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # forecast_cache
    op.create_table(
        'forecast_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=False),
        sa.Column('variety', sa.String(length=100), nullable=False),
        sa.Column('cropping_type', sa.String(length=50), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('predicted_yield', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('lower_bound', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('upper_bound', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # prediction_history
    op.create_table(
        'prediction_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=False),
        sa.Column('variety', sa.String(length=100), nullable=False),
        sa.Column('cropping_type', sa.String(length=50), nullable=False),
        sa.Column('predicted_yield', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('lower_bound', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('upper_bound', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # advisory_history
    op.create_table(
        'advisory_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prediction_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=False),
        sa.Column('variety', sa.String(length=100), nullable=False),
        sa.Column('cropping_type', sa.String(length=50), nullable=False),
        sa.Column('predicted_yield', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('lower_bound', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('upper_bound', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('risk_score', sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column('advisory_text', sa.Text(), nullable=False),
        sa.Column('action_items', sa.Text(), nullable=False),
        sa.Column('warning_alerts', sa.Text(), nullable=True),
        sa.Column('llm_provider', sa.String(length=50), nullable=False),
        sa.Column('llm_model', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['prediction_id'], ['prediction_history.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # ndvi_cache
    op.create_table(
        'ndvi_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_name', sa.String(length=100), nullable=False),
        sa.Column('ndvi_value', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('vegetation_status', sa.String(length=50), nullable=True),
        sa.Column('computed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_name')
    )

    # explainability_cache
    op.create_table(
        'explainability_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prediction_id', sa.Integer(), nullable=False),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=False),
        sa.Column('contributions', postgresql.JSONB(), nullable=False),
        sa.Column('top_factor', sa.String(length=50), nullable=False),
        sa.Column('summary_text_bn', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prediction_id')
    )

    # mixed_cropping_mappings
    op.create_table(
        'mixed_cropping_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('primary_crop', sa.String(length=100), nullable=False),
        sa.Column('secondary_crop', sa.String(length=100), nullable=False),
        sa.Column('mixing_ratio', sa.String(length=50), nullable=False),
        sa.Column('yield_adjustment', sa.Numeric(precision=6, scale=4), nullable=False, server_default='1.0'),
        sa.PrimaryKeyConstraint('id')
    )

    # risk_thresholds
    op.create_table(
        'risk_thresholds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('metric', sa.String(length=50), nullable=False),
        sa.Column('low_threshold', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('medium_threshold', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('high_threshold', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('description_bn', sa.Text(), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # processed_dataset
    op.create_table(
        'processed_dataset',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('rows', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # user_preferences
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('last_crop', sa.String(length=100), nullable=True),
        sa.Column('last_region', sa.String(length=100), nullable=True),
        sa.Column('last_variety', sa.String(length=100), nullable=True),
        sa.Column('last_cropping_type', sa.String(length=50), nullable=True),
        sa.Column('theme', sa.String(length=20), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('user_preferences')
    op.drop_table('processed_dataset')
    op.drop_table('risk_thresholds')
    op.drop_table('mixed_cropping_mappings')
    op.drop_table('explainability_cache')
    op.drop_table('ndvi_cache')
    op.drop_table('advisory_history')
    op.drop_table('prediction_history')
    op.drop_table('forecast_cache')
    op.drop_table('model_metadata')
    op.drop_table('historical_yield')
    op.drop_table('crop_varieties')
    op.drop_table('regions')
    op.drop_table('crops')
    op.drop_table('user_sessions')
    op.drop_table('users')
    op.drop_table('roles')