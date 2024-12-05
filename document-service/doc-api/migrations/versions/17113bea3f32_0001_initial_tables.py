"""0001_initial_tables

Revision ID: 17113bea3f32
Revises: 
Create Date: 2024-08-01 15:52:23.435152

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import Sequence, CreateSequence, DropSequence  # Added manually.

# revision identifiers, used by Alembic.
revision = '17113bea3f32'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### Manually create sequences and add them to pk columns. ###
    op.execute(CreateSequence(Sequence('service_doc_id_seq', start=100000, increment=1)))
    op.execute(CreateSequence(Sequence('document_number_seq', start=100000000, increment=1)))
    op.execute(CreateSequence(Sequence('document_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('request_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('user_id_seq', start=1, increment=1)))

    # ### commands auto generated by Alembic - please adjust! ###
    document_classes = op.create_table('document_classes',
    sa.Column('document_class', postgresql.ENUM('COOP', 'CORP', 'FIRM', 'LP_LLP', 'MHR', 'NR', 'OTHER', 'PPR', 'SOCIETY', 'XP', 'DELETED', name='documentclass'), nullable=False),
    sa.Column('document_class_desc', sa.String(length=100), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('scanning_owner_type', sa.String(length=20), nullable=True),
    sa.Column('schedule_number', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('document_class')
    )
    request_types = op.create_table('request_types',
    sa.Column('request_type', postgresql.ENUM('ADD', 'GET', 'PENDING', 'REPLACE', 'UPDATE', 'DELETE', name='requesttype'), nullable=False),
    sa.Column('request_type_desc', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('request_type')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), sa.Sequence('user_id_seq'), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('username', sa.String(length=1000), nullable=False),
    sa.Column('sub', sa.String(length=36), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=True),
    sa.Column('firstname', sa.String(length=1000), nullable=True),
    sa.Column('lastname', sa.String(length=1000), nullable=True),
    sa.Column('email', sa.String(length=1024), nullable=True),
    sa.Column('iss', sa.String(length=1024), nullable=True),
    sa.Column('idp_userid', sa.String(length=256), nullable=True),
    sa.Column('login_source', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sub')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_idp_userid'), ['idp_userid'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=False)

    document_types = op.create_table('document_types',
    sa.Column('document_type', postgresql.ENUM('REG_101', 'REG_102', 'REG_103', 'MHR_MISC', 'ABAN', 'ADDI', 'AFFE', 'ATTA', 'BANK', 'BCLC', 'CAU', 'CAUC', 'CAUE', 'COMP', 'COUR', 'DEAT', 'DNCH', 'EXMN', 'EXNR', 'EXRE', 'EXRS', 'FORE', 'FZE', 'GENT', 'LETA', 'MAID', 'MAIL', 'MARR', 'NAMV', 'NCAN', 'NCON', 'NPUB', 'NRED', 'PDEC', 'PUBA', 'REBU', 'REGC', 'REIV', 'REPV', 'REST', 'STAT', 'SZL', 'TAXN', 'TAXS', 'THAW', 'TRAN', 'VEST', 'WHAL', 'WILL', 'COOP_MISC', 'CORP_MISC', 'FIRM_MISC', 'NR_MISC', 'PPR_MISC', 'SOC_MISC', 'COFI', 'DISS', 'DISD', 'ATTN', 'FRMA', 'AMLO', 'CNTA', 'CNTI', 'CNTO', 'COFF', 'COSD', 'AMLG', 'AMAL', 'RSRI', 'ASNU', 'LPRG', 'FILE', 'CNVF', 'COPN', 'MHSP', 'FNCH', 'CONS', 'PPRS', 'PPRC', 'ADDR', 'ANNR', 'CORR', 'DIRS', 'CORC', 'SOCF', 'CERT', 'LTR', 'CLW', 'BYLW', 'CNST', 'CONT', 'SYSR', 'ADMN', 'RSLN', 'AFDV', 'SUPP', 'MNOR', 'FINM', 'APCO', 'RPTP', 'DAT', 'BYLT', 'CNVS', 'CRTO', 'MEM', 'PRE', 'REGO', 'PLNA', 'REGN', 'FINC', 'BCGT', 'CHNM', 'OTP', 'LP_LLP_MISC', 'XP_MISC', 'PPR', 'LHS', 'RGS', 'HSR', 'RPL', 'FINS', 'CORSP', 'DELETED', 'COOP_RULES', 'COOP_MEMORANDUM', 'CORP_AFFIDAVIT', 'DIRECTOR_AFFIDAVIT', 'PART', name='documenttype'), nullable=False),
    sa.Column('document_class', postgresql.ENUM('COOP', 'CORP', 'FIRM', 'LP_LLP', 'MHR', 'NR', 'OTHER', 'PPR', 'SOCIETY', 'XP', 'DELETED', name='documentclass'), nullable=False),
    sa.Column('document_type_desc', sa.String(length=100), nullable=False),
    sa.Column('product', sa.String(length=20), nullable=False),
    sa.Column('doc_id_required', sa.Boolean(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('application_id', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['document_class'], ['document_classes.document_class'], ),
    sa.PrimaryKeyConstraint('document_type')
    )
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_service_id', sa.String(length=20), nullable=False),
    sa.Column('add_ts', sa.DateTime(), nullable=False),
    sa.Column('consumer_document_id', sa.String(length=20), nullable=False),
    sa.Column('consumer_identifier', sa.String(length=20), nullable=True),
    sa.Column('consumer_filename', sa.String(length=1000), nullable=True),
    sa.Column('consumer_filing_date', sa.DateTime(), nullable=True),
    sa.Column('scan_date', sa.DateTime(), nullable=True),
    sa.Column('doc_storage_url', sa.String(length=1000), nullable=True),
    sa.Column('document_type', postgresql.ENUM('REG_101', 'REG_102', 'REG_103', 'MHR_MISC', 'ABAN', 'ADDI', 'AFFE', 'ATTA', 'BANK', 'BCLC', 'CAU', 'CAUC', 'CAUE', 'COMP', 'COUR', 'DEAT', 'DNCH', 'EXMN', 'EXNR', 'EXRE', 'EXRS', 'FORE', 'FZE', 'GENT', 'LETA', 'MAID', 'MAIL', 'MARR', 'NAMV', 'NCAN', 'NCON', 'NPUB', 'NRED', 'PDEC', 'PUBA', 'REBU', 'REGC', 'REIV', 'REPV', 'REST', 'STAT', 'SZL', 'TAXN', 'TAXS', 'THAW', 'TRAN', 'VEST', 'WHAL', 'WILL', 'COOP_MISC', 'CORP_MISC', 'FIRM_MISC', 'NR_MISC', 'PPR_MISC', 'SOC_MISC', 'COFI', 'DISS', 'DISD', 'ATTN', 'FRMA', 'AMLO', 'CNTA', 'CNTI', 'CNTO', 'COFF', 'COSD', 'AMLG', 'AMAL', 'RSRI', 'ASNU', 'LPRG', 'FILE', 'CNVF', 'COPN', 'MHSP', 'FNCH', 'CONS', 'PPRS', 'PPRC', 'ADDR', 'ANNR', 'CORR', 'DIRS', 'CORC', 'SOCF', 'CERT', 'LTR', 'CLW', 'BYLW', 'CNST', 'CONT', 'SYSR', 'ADMN', 'RSLN', 'AFDV', 'SUPP', 'MNOR', 'FINM', 'APCO', 'RPTP', 'DAT', 'BYLT', 'CNVS', 'CRTO', 'MEM', 'PRE', 'REGO', 'PLNA', 'REGN', 'FINC', 'BCGT', 'CHNM', 'OTP', 'LP_LLP_MISC', 'XP_MISC', 'PPR', 'LHS', 'RGS', 'HSR', 'RPL', 'FINS', 'CORSP', 'DELETED', 'COOP_RULES', 'COOP_MEMORANDUM', 'CORP_AFFIDAVIT', 'DIRECTOR_AFFIDAVIT', 'PART', name='documenttype'), nullable=False),
    sa.ForeignKeyConstraint(['document_type'], ['document_types.document_type'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('document_service_id')
    )
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_documents_add_ts'), ['add_ts'], unique=False)
        batch_op.create_index(batch_op.f('ix_documents_consumer_document_id'), ['consumer_document_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_documents_consumer_filing_date'), ['consumer_filing_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_documents_consumer_identifier'), ['consumer_identifier'], unique=False)

    op.create_table('document_requests',
    sa.Column('id', sa.Integer(), sa.Sequence('request_id_seq'), nullable=False),
    sa.Column('request_ts', sa.DateTime(), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=True),
    sa.Column('username', sa.String(length=1000), nullable=True),
    sa.Column('request_data', sa.JSON(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('status_message', sa.String(length=4000), nullable=True),
    sa.Column('request_type', postgresql.ENUM('ADD', 'GET', 'PENDING', 'REPLACE', 'UPDATE', 'DELETE', name='requesttype'), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['request_type'], ['request_types.request_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('document_requests', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_document_requests_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_document_requests_document_id'), ['document_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_document_requests_request_ts'), ['request_ts'], unique=False)

    public_get_service_doc_id = PGFunction(
        schema="public",
        signature="get_service_doc_id()",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    BEGIN\n        RETURN 'DS' || trim(to_char(nextval('service_doc_id_seq'), '0000000000'));\n    END\n    ;\n    $$"
    )
    op.create_entity(public_get_service_doc_id)

    public_get_document_number = PGFunction(
        schema="public",
        signature="get_document_number()",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    BEGIN\n        RETURN trim(to_char(nextval('document_number_seq'), '0000000000'));\n    END\n    ;\n    $$"
    )
    op.create_entity(public_get_document_number)

    # Type table inserts begin
    op.bulk_insert(
        request_types,
        [
            {"request_type": "ADD", "request_type_desc": "Add a new document."},
            {"request_type": "PENDING", "request_type_desc": "Create information about a document without uploading the document."},
            {"request_type": "GET", "request_type_desc": "Fetch an existing document."},
            {"request_type": "REPLACE", "request_type_desc": "Staff only replace existing document uploaded in error."},
            {"request_type": "UPDATE", "request_type_desc": "Add/replace meta data associated with a document."},
            {"request_type": "DELETE", "request_type_desc": "Permanently delete a single document from storage."},
        ],
    )
    op.bulk_insert(
        document_classes,
        [
            {"document_class": "COOP", "document_class_desc": "Cooperatives", "active": True, "scanning_owner_type": "COOP", "schedule_number": 0},
            {"document_class": "CORP", "document_class_desc": "Corporations", "active": True, "scanning_owner_type": "CORP", "schedule_number": 0},
            {"document_class": "FIRM", "document_class_desc": "Firms", "active": True, "scanning_owner_type": "FIRM", "schedule_number": 0},
            {"document_class": "LP_LLP", "document_class_desc": "Limited Partnerships/Limited Liability Partnerships", "active": False, "scanning_owner_type": "LLP", "schedule_number": 0},
            {"document_class": "MHR", "document_class_desc": "Manufactured Homes", "active": True, "scanning_owner_type": "MHR", "schedule_number": 0},
            {"document_class": "NR", "document_class_desc": "Name Requests", "active": True, "scanning_owner_type": "NR", "schedule_number": 0},
            {"document_class": "OTHER", "document_class_desc": "Other", "active": True, "scanning_owner_type": "OT", "schedule_number": 0},
            {"document_class": "PPR", "document_class_desc": "Personal Property Registry", "active": True, "scanning_owner_type": "PPR", "schedule_number": 0},
            {"document_class": "SOCIETY", "document_class_desc": "Societies", "active": True, "scanning_owner_type": "SOC", "schedule_number": 0},
            {"document_class": "XP", "document_class_desc": "Extraprovincial Registrations", "active": False, "scanning_owner_type": "XP", "schedule_number": 0},
            {"document_class": "DELETED", "document_class_desc": "Removed, marked as deleted", "active": False, "scanning_owner_type": "DELETED", "schedule_number": 0},
        ],
    )
    op.bulk_insert(
        document_types,
        [
            {"document_type": "MHR_MISC", "document_class": "MHR", "document_type_desc": "MHR miscellaneous documents", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REG_101", "document_class": "MHR", "document_type_desc": "MANUFACTURED HOME REGISTRATION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REG_102", "document_class": "MHR", "document_type_desc": "DECAL REPLACEMENT", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REG_103", "document_class": "MHR", "document_type_desc": "TRANSPORT PERMIT", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "ABAN", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO ABANDONMENT AND SALE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "ADDI", "document_class": "MHR", "document_type_desc": "ADDITION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "AFFE", "document_class": "MHR", "document_type_desc": "TRANSFER TO EXECUTOR – ESTATE UNDER $25,000 WITH WILL", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "ATTA", "document_class": "MHR", "document_type_desc": "ATTACHMENT", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "BANK", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO BANKRUPTCY", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "CAU", "document_class": "MHR", "document_type_desc": "NOTICE OF CAUTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "CAUC", "document_class": "MHR", "document_type_desc": "CONTINUED NOTICE OF CAUTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "CAUE", "document_class": "MHR", "document_type_desc": "EXTENSION TO NOTICE OF CAUTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "COMP", "document_class": "MHR", "document_type_desc": "CERTIFICATE OF COMPANIES", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "COUR", "document_class": "MHR", "document_type_desc": "COURT RESCIND ORDER", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "DEAT", "document_class": "MHR", "document_type_desc": "TRANSFER TO SURVIVING JOINT TENANT(S)", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "DNCH", "document_class": "MHR", "document_type_desc": "DECLARATION OF NAME CHANGE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "EXMN", "document_class": "MHR", "document_type_desc": "MANUFACTURED EXEMPTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "EXNR", "document_class": "MHR", "document_type_desc": "NON-RESIDENTIAL EXEMPTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "EXRE", "document_class": "MHR", "document_type_desc": "MANUFACTURED HOME RE-REGISTRATION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "EXRS", "document_class": "MHR", "document_type_desc": "RESIDENTIAL EXEMPTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "FORE", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO FORECLOSURE ORDER", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "FZE", "document_class": "MHR", "document_type_desc": "REGISTRARS FREEZE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "GENT", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO GENERAL TRANSMISSION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "LETA", "document_class": "MHR", "document_type_desc": "TRANSFER TO ADMINISTRATOR – GRANT OF PROBATE WITH NO WILL", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "MAID", "document_class": "MHR", "document_type_desc": "MAIDEN NAME", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "MAIL", "document_class": "MHR", "document_type_desc": "MAILING ADDRESS", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "MARR", "document_class": "MHR", "document_type_desc": "MARRIAGE CERTIFICATE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "MHSP", "document_class": "MHR", "document_type_desc": "MH Supporting Documentation", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "NAMV", "document_class": "MHR", "document_type_desc": "CERTIFICATE OF VITAL STATS", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "NCAN", "document_class": "MHR", "document_type_desc": "CANCEL NOTE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "NCON", "document_class": "MHR", "document_type_desc": "CONFIDENTIAL NOTE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "NPUB", "document_class": "MHR", "document_type_desc": "PUBLIC NOTE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "NRED", "document_class": "MHR", "document_type_desc": "NOTICE OF REDEMPTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "PUBA", "document_class": "MHR", "document_type_desc": "PUBLIC AMENDMENT", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REBU", "document_class": "MHR", "document_type_desc": "REBUILT", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REGC", "document_class": "MHR", "document_type_desc": "REGISTRAR'S CORRECTION", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REIV", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO REPOSSESSION - INVOLUNTARY", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REPV", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO REPOSSESSION - VOLUNTARY", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "REST", "document_class": "MHR", "document_type_desc": "RESTRAINING ORDER", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "STAT", "document_class": "MHR", "document_type_desc": "REGISTERED LOCATION CHANGE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "SZL", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO SEIZURE UNDER LAND ACT", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "TAXN", "document_class": "MHR", "document_type_desc": "NOTICE OF TAX SALE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "TAXS", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO TAX SALE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "THAW", "document_class": "MHR", "document_type_desc": "REMOVE FREEZE", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "TRAN", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO SALE OR GIFT", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "VEST", "document_class": "MHR", "document_type_desc": "TRANSFER DUE TO VESTING ORDER", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "WHAL", "document_class": "MHR", "document_type_desc": "WAREHOUSEMAN LIEN", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "WILL", "document_class": "MHR", "document_type_desc": "TRANSFER TO EXECUTOR - GRANT OF PROBATE WITH WILL", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
            {"document_type": "COFI", "document_class": "COOP", "document_type_desc": "Correction Filing", "product": "business", "doc_id_required": False, "active": True, "application_id": "COOP"},
            {"document_type": "COOP_MISC", "document_class": "COOP", "document_type_desc": "Cooperatives miscellaneous documents", "product": "business", "doc_id_required": False, "active": False, "application_id": "COOP"},
            {"document_type": "DISS", "document_class": "CORP", "document_type_desc": "Dissolution Due to Death", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "DISD", "document_class": "CORP", "document_type_desc": "Dissolution Delays", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "ATTN", "document_class": "CORP", "document_type_desc": "Attorney", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "FRMA", "document_class": "CORP", "document_type_desc": "Form 2's Address Change for Corps", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "AMLO", "document_class": "CORP", "document_type_desc": "Amalgamation Out", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CNTA", "document_class": "CORP", "document_type_desc": "Continuation in Authorization", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CNTI", "document_class": "CORP", "document_type_desc": "Continuation In", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CNTO", "document_class": "CORP", "document_type_desc": "Continuation Out", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "COFF", "document_class": "CORP", "document_type_desc": "CORPS Filed Forms", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "COSD", "document_class": "CORP", "document_type_desc": "CORPS Supporting Documentation", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "AMLG", "document_class": "CORP", "document_type_desc": "Amalgamations", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "AMAL", "document_class": "CORP", "document_type_desc": "Update Due to Amalgamation", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "RSRI", "document_class": "CORP", "document_type_desc": "Restoration/Reinstatement", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "ASNU", "document_class": "CORP", "document_type_desc": "Assumed Name Undertaking", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "LPRG", "document_class": "CORP", "document_type_desc": "LP and LLP Registration", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "FILE", "document_class": "CORP", "document_type_desc": "COLIN Filing", "product": "business", "doc_id_required": False, "active": True, "application_id": "COLIIN"},
            {"document_type": "CORP_MISC", "document_class": "CORP", "document_type_desc": "Corporations miscellaneous documents", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CNVF", "document_class": "FIRM", "document_type_desc": "Conversion of Firm", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "COPN", "document_class": "FIRM", "document_type_desc": "Change of Proprietor's Name", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "FIRM_MISC", "document_class": "FIRM", "document_type_desc": "Firms miscellaneous documents", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CONS", "document_class": "NR", "document_type_desc": "NR Consent Letter", "product": "nro", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "NR_MISC", "document_class": "NR", "document_type_desc": "Name requests miscellaneous documents", "product": "nro", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "FNCH", "document_class": "PPR", "document_type_desc": "Finance Change Statements/Partial Discharges", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "PPRS", "document_class": "PPR", "document_type_desc": "PPR Search", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "PPRC", "document_class": "PPR", "document_type_desc": "PPR Secure Party Codes", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "PPR_MISC", "document_class": "PPR", "document_type_desc": "PPR miscellaneous documents", "product": "ppr", "doc_id_required": False, "active": False, "application_id": "PPR"},
            {"document_type": "ADDR", "document_class": "SOCIETY", "document_type_desc": "Address", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "ANNR", "document_class": "SOCIETY", "document_type_desc": "Annual Report", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CORR", "document_class": "SOCIETY", "document_type_desc": "Correspondence", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "DIRS", "document_class": "SOCIETY", "document_type_desc": "Directors", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CORC", "document_class": "SOCIETY", "document_type_desc": "Corrections", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "SOCF", "document_class": "SOCIETY", "document_type_desc": "Society Filing", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "SOC_MISC", "document_class": "SOCIETY", "document_type_desc": "Societies miscellaneous documents", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CERT", "document_class": "OTHER", "document_type_desc": "Certificates", "product": "business", "doc_id_required": False, "active": True, "application_id": "CLW"},
            {"document_type": "LTR", "document_class": "OTHER", "document_type_desc": "Letter Templates", "product": "business", "doc_id_required": False, "active": True, "application_id": "CLW"},
            {"document_type": "CLW", "document_class": "OTHER", "document_type_desc": "Client Letters", "product": "business", "doc_id_required": False, "active": True, "application_id": "CLW"},
            {"document_type": "BYLW", "document_class": "OTHER", "document_type_desc": "Bylaw", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "CNST", "document_class": "OTHER", "document_type_desc": "Constitution", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "CONT", "document_class": "OTHER", "document_type_desc": "Consent", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "SYSR", "document_class": "OTHER", "document_type_desc": "System is the record", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "ADMN", "document_class": "OTHER", "document_type_desc": "Administration", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "RSLN", "document_class": "OTHER", "document_type_desc": "Resolution Document", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "AFDV", "document_class": "OTHER", "document_type_desc": "Affidavit Document", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "SUPP", "document_class": "OTHER", "document_type_desc": "Supporting Documents", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "MNOR", "document_class": "OTHER", "document_type_desc": "Minister's Order", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "FINM", "document_class": "OTHER", "document_type_desc": "Financial Management", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "APCO", "document_class": "OTHER", "document_type_desc": "Application to Correct the Registry", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "RPTP", "document_class": "OTHER", "document_type_desc": "Report of Payments", "product": "business", "doc_id_required": False, "active": True, "application_id": "REGI"},
            {"document_type": "DAT", "document_class": "OTHER", "document_type_desc": "DAT or CAT", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "BYLT", "document_class": "OTHER", "document_type_desc": "Bylaw Alterations", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CNVS", "document_class": "OTHER", "document_type_desc": "Conversions", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CRTO", "document_class": "OTHER", "document_type_desc": "Court Orders", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "MEM", "document_class": "OTHER", "document_type_desc": "Membership", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "PRE", "document_class": "OTHER", "document_type_desc": "Pre Image Documents", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "REGO", "document_class": "OTHER", "document_type_desc": "Registrar's Order", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "PLNA", "document_class": "OTHER", "document_type_desc": "Plan of Arrangements", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "REGN", "document_class": "OTHER", "document_type_desc": "Registrar's Notation", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "FINC", "document_class": "OTHER", "document_type_desc": "Financial", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "BCGT", "document_class": "OTHER", "document_type_desc": "BC Gazette", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "CHNM", "document_class": "OTHER", "document_type_desc": "Change Of Name", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "OTP", "document_class": "OTHER", "document_type_desc": "Other", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "LP_LLP_MISC", "document_class": "LP_LLP", "document_type_desc": "LP/LLP miscellaneous documents", "product": "business", "doc_id_required": False, "active": False, "application_id": "SCAN"},
            {"document_type": "XP_MISC", "document_class": "XP", "document_type_desc": "Extraprovincial miscellaneous documents", "product": "business", "doc_id_required": False, "active": False, "application_id": "SCAN"},
            {"document_type": "CORSP", "document_class": "MHR", "document_type_desc": "Correspondence", "product": "mhr", "doc_id_required": False, "active": False, "application_id": "MHR"},
            {"document_type": "PPR", "document_class": "PPR", "document_type_desc": "PPR (Register Discharges)", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "LHS", "document_class": "PPR", "document_type_desc": "PPR Letter Head Search,", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "RGS", "document_class": "PPR", "document_type_desc": "PPR Regular Search", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "HSR", "document_class": "PPR", "document_type_desc": "PPR Historical Search", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "RPL", "document_class": "PPR", "document_type_desc": "PPR Repairer Liens", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "FINS", "document_class": "PPR", "document_type_desc": "PPR Financial Statement", "product": "ppr", "doc_id_required": False, "active": True, "application_id": "PPR"},
            {"document_type": "DELETED", "document_class": "DELETED", "document_type_desc": "Removed, marked as deleted.", "product": "*", "doc_id_required": False, "active": False, "application_id": "ALL"},
            {"document_type": "COOP_RULES", "document_class": "COOP", "document_type_desc": "Cooperative Rules", "product": "business", "doc_id_required": False, "active": False, "application_id": "COOP"},
            {"document_type": "COOP_MEMORANDUM", "document_class": "COOP", "document_type_desc": "Cooperative Memorandum", "product": "business", "doc_id_required": False, "active": False, "application_id": "COOP"},
            {"document_type": "CORP_AFFIDAVIT", "document_class": "CORP", "document_type_desc": "Affidavit", "product": "business", "doc_id_required": False, "active": False, "application_id": "SCAN"},
            {"document_type": "DIRECTOR_AFFIDAVIT", "document_class": "CORP", "document_type_desc": "Director Affidavit", "product": "business", "doc_id_required": False, "active": False, "application_id": "SCAN"},
            {"document_type": "PART", "document_class": "FIRM", "document_type_desc": "Partnerships", "product": "business", "doc_id_required": False, "active": True, "application_id": "SCAN"},
            {"document_type": "BCLC", "document_class": "MHR", "document_type_desc": "BCAA LOC. Change", "product": "mhr", "doc_id_required": False, "active": True, "application_id": "MHR"},
        ],
    )

    # Type table inserts end

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    public_get_document_number = PGFunction(
        schema="public",
        signature="get_document_number()",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    BEGIN\n        RETURN trim(to_char(nextval('document_number_seq'), '0000000000'));\n    END\n    ;\n    $$"
    )
    op.drop_entity(public_get_document_number)

    public_get_service_doc_id = PGFunction(
        schema="public",
        signature="get_service_doc_id()",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    BEGIN\n        RETURN 'DS' || trim(to_char(nextval('service_doc_id_seq'), '0000000000'));\n    END\n    ;\n    $$"
    )
    op.drop_entity(public_get_service_doc_id)

    with op.batch_alter_table('document_requests', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_document_requests_request_ts'))
        batch_op.drop_index(batch_op.f('ix_document_requests_document_id'))
        batch_op.drop_index(batch_op.f('ix_document_requests_account_id'))

    op.drop_table('document_requests')
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_documents_consumer_identifier'))
        batch_op.drop_index(batch_op.f('ix_documents_consumer_filing_date'))
        batch_op.drop_index(batch_op.f('ix_documents_consumer_document_id'))
        batch_op.drop_index(batch_op.f('ix_documents_add_ts'))

    op.drop_table('documents')
    op.drop_table('document_types')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_idp_userid'))

    op.drop_table('users')
    op.drop_table('request_types')
    op.drop_table('document_classes')

    # Manually added drop sequence commands ###
    op.execute(DropSequence(Sequence('service_doc_id_seq')))
    op.execute(DropSequence(Sequence('document_number_seq')))
    op.execute(DropSequence(Sequence('document_id_seq')))
    op.execute(DropSequence(Sequence('request_id_seq')))
    op.execute(DropSequence(Sequence('user_id_seq')))
    # ### end Alembic commands ###
