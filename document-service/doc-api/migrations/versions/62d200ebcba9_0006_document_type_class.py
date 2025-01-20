"""0006_document_type_class

Revision ID: 62d200ebcba9
Revises: e26474330753
Create Date: 2024-12-05 13:23:33.661185

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '62d200ebcba9'
down_revision = 'e26474330753'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    document_type_classes = op.create_table('document_type_classes',
    sa.Column('document_type', postgresql.ENUM('REG_101', 'REG_102', 'REG_103', 'MHR_MISC', 'ABAN', 'ADDI', 'AFFE', 'ATTA', 'BANK', 'BCLC', 'CAU', 'CAUC', 'CAUE', 'COMP', 'COUR', 'DEAT', 'DNCH', 'EXMN', 'EXNR', 'EXRE', 'EXRS', 'FORE', 'FZE', 'GENT', 'LETA', 'MAID', 'MAIL', 'MARR', 'NAMV', 'NCAN', 'NCON', 'NPUB', 'NRED', 'PDEC', 'PUBA', 'REBU', 'REGC', 'REIV', 'REPV', 'REST', 'STAT', 'SZL', 'TAXN', 'TAXS', 'THAW', 'TRAN', 'VEST', 'WHAL', 'WILL', 'COOP_MISC', 'CORP_MISC', 'FIRM_MISC', 'LP_LLP_MISC', 'NR_MISC', 'PPR_MISC', 'SOC_MISC', 'XP_MISC', 'COFI', 'DISS', 'DISD', 'ATTN', 'FRMA', 'AMLO', 'CNTA', 'CNTI', 'CNTO', 'COFF', 'COSD', 'AMLG', 'AMAL', 'RSRI', 'ASNU', 'LPRG', 'FILE', 'CNVF', 'COPN', 'MHSP', 'FNCH', 'CONS', 'PPRS', 'PPRC', 'ADDR', 'ANNR', 'CORR', 'DIRS', 'CORC', 'SOCF', 'CERT', 'LTR', 'CLW', 'BYLW', 'CNST', 'CONT', 'SYSR', 'ADMN', 'RSLN', 'AFDV', 'SUPP', 'MNOR', 'FINM', 'APCO', 'RPTP', 'DAT', 'BYLT', 'CNVS', 'CRTO', 'MEM', 'PRE', 'REGO', 'PLNA', 'REGN', 'FINC', 'BCGT', 'CHNM', 'OTP', 'CORSP', 'PPR', 'LHS', 'RGS', 'HSR', 'RPL', 'FINS', 'DELETED', 'COOP_RULES', 'COOP_MEMORANDUM', 'CORP_AFFIDAVIT', 'DIRECTOR_AFFIDAVIT', 'PART', 'REG_103E', 'AMEND_PERMIT', 'CANCEL_PERMIT', 'REREGISTER_C', 'MEAM', 'COU', 'CRT', 'INV', 'NATB', 'NWP', name='documenttype', create_type=False), nullable=False),
    sa.Column('document_class', postgresql.ENUM('COOP', 'CORP', 'DELETED', 'FIRM', 'LP_LLP', 'MHR', 'NR', 'OTHER', 'PPR', 'SOCIETY', 'XP', name='documentclass', create_type=False), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['document_class'], ['document_classes.document_class'], ),
    sa.ForeignKeyConstraint(['document_type'], ['document_types.document_type'], ),
    sa.PrimaryKeyConstraint('document_type', 'document_class')
    )
    with op.batch_alter_table('document_type_classes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_document_type_classes_document_class'), ['document_class'], unique=False)
        batch_op.create_index(batch_op.f('ix_document_type_classes_document_type'), ['document_type'], unique=False)

    with op.batch_alter_table('document_types', schema=None) as batch_op:
        batch_op.drop_constraint('document_types_document_class_fkey', type_='foreignkey')
        batch_op.drop_column('document_class')

    op.bulk_insert(
        document_type_classes,
        [
            {"document_type": "COFI", "document_class": "COOP", "active": True},
            {"document_type": "CONT", "document_class": "COOP", "active": True},
            {"document_type": "COOP_MEMORANDUM", "document_class": "COOP", "active": True},
            {"document_type": "COOP_MISC", "document_class": "COOP", "active": True},
            {"document_type": "COOP_RULES", "document_class": "COOP", "active": True},
            {"document_type": "CORR", "document_class": "COOP", "active": True},
            {"document_type": "FILE", "document_class": "COOP", "active": True},
            {"document_type": "ADDR", "document_class": "CORP", "active": True},
            {"document_type": "AMAL", "document_class": "CORP", "active": True},
            {"document_type": "AMLG", "document_class": "CORP", "active": True},
            {"document_type": "AMLO", "document_class": "CORP", "active": True},
            {"document_type": "ANNR", "document_class": "CORP", "active": True},
            {"document_type": "APCO", "document_class": "CORP", "active": True},
            {"document_type": "ASNU", "document_class": "CORP", "active": True},
            {"document_type": "ATTN", "document_class": "CORP", "active": True},
            {"document_type": "CERT", "document_class": "CORP", "active": True},
            {"document_type": "CLW", "document_class": "CORP", "active": True},
            {"document_type": "CNTA", "document_class": "CORP", "active": True},
            {"document_type": "CNTI", "document_class": "CORP", "active": True},
            {"document_type": "CNTO", "document_class": "CORP", "active": True},
            {"document_type": "CNVS", "document_class": "CORP", "active": True},
            {"document_type": "COFF", "document_class": "CORP", "active": True},
            {"document_type": "COMP", "document_class": "CORP", "active": True},
            {"document_type": "CONT", "document_class": "CORP", "active": True},
            {"document_type": "CORC", "document_class": "CORP", "active": True},
            {"document_type": "CORP_AFFIDAVIT", "document_class": "CORP", "active": True},
            {"document_type": "CORP_MISC", "document_class": "CORP", "active": True},
            {"document_type": "CORR", "document_class": "CORP", "active": True},
            {"document_type": "COSD", "document_class": "CORP", "active": True},
            {"document_type": "CRTO", "document_class": "CORP", "active": True},
            {"document_type": "DIRECTOR_AFFIDAVIT", "document_class": "CORP", "active": True},
            {"document_type": "DIRS", "document_class": "CORP", "active": True},
            {"document_type": "DISD", "document_class": "CORP", "active": True},
            {"document_type": "FILE", "document_class": "CORP", "active": True},
            {"document_type": "FRMA", "document_class": "CORP", "active": True},
            {"document_type": "LTR", "document_class": "CORP", "active": True},
            {"document_type": "MNOR", "document_class": "CORP", "active": True},
            {"document_type": "PLNA", "document_class": "CORP", "active": True},
            {"document_type": "REGN", "document_class": "CORP", "active": True},
            {"document_type": "REGO", "document_class": "CORP", "active": True},
            {"document_type": "RSRI", "document_class": "CORP", "active": True},
            {"document_type": "SUPP", "document_class": "CORP", "active": True},
            {"document_type": "SYSR", "document_class": "CORP", "active": True},
            {"document_type": "ADDR", "document_class": "FIRM", "active": True},
            {"document_type": "CNVF", "document_class": "FIRM", "active": True},
            {"document_type": "CONT", "document_class": "FIRM", "active": True},
            {"document_type": "COPN", "document_class": "FIRM", "active": True},
            {"document_type": "CORR", "document_class": "FIRM", "active": True},
            {"document_type": "DISS", "document_class": "FIRM", "active": True},
            {"document_type": "FILE", "document_class": "FIRM", "active": True},
            {"document_type": "FIRM_MISC", "document_class": "FIRM", "active": True},
            {"document_type": "PART", "document_class": "FIRM", "active": True},
            {"document_type": "ANNR", "document_class": "LP_LLP", "active": True},
            {"document_type": "ATTN", "document_class": "LP_LLP", "active": True},
            {"document_type": "CHNM", "document_class": "LP_LLP", "active": True},
            {"document_type": "CNVF", "document_class": "LP_LLP", "active": True},
            {"document_type": "CONT", "document_class": "LP_LLP", "active": True},
            {"document_type": "CORR", "document_class": "LP_LLP", "active": True},
            {"document_type": "FILE", "document_class": "LP_LLP", "active": True},
            {"document_type": "LP_LLP_MISC", "document_class": "LP_LLP", "active": True},
            {"document_type": "LPRG", "document_class": "LP_LLP", "active": True},
            {"document_type": "ABAN", "document_class": "MHR", "active": True},
            {"document_type": "ADDI", "document_class": "MHR", "active": True},
            {"document_type": "ADDR", "document_class": "MHR", "active": True},
            {"document_type": "AFDV", "document_class": "MHR", "active": True},
            {"document_type": "AFFE", "document_class": "MHR", "active": True},
            {"document_type": "ATTA", "document_class": "MHR", "active": True},
            {"document_type": "BANK", "document_class": "MHR", "active": True},
            {"document_type": "BCLC", "document_class": "MHR", "active": True},
            {"document_type": "CAU", "document_class": "MHR", "active": True},
            {"document_type": "CAUC", "document_class": "MHR", "active": True},
            {"document_type": "CAUE", "document_class": "MHR", "active": True},
            {"document_type": "CONT", "document_class": "MHR", "active": True},
            {"document_type": "CORR", "document_class": "MHR", "active": True},
            {"document_type": "CORSP", "document_class": "MHR", "active": True},
            {"document_type": "COUR", "document_class": "MHR", "active": True},
            {"document_type": "CRTO", "document_class": "MHR", "active": True},
            {"document_type": "DEAT", "document_class": "MHR", "active": True},
            {"document_type": "DNCH", "document_class": "MHR", "active": True},
            {"document_type": "EXMN", "document_class": "MHR", "active": True},
            {"document_type": "EXNR", "document_class": "MHR", "active": True},
            {"document_type": "EXRE", "document_class": "MHR", "active": True},
            {"document_type": "EXRS", "document_class": "MHR", "active": True},
            {"document_type": "FNCH", "document_class": "MHR", "active": True},
            {"document_type": "FORE", "document_class": "MHR", "active": True},
            {"document_type": "FZE", "document_class": "MHR", "active": True},
            {"document_type": "GENT", "document_class": "MHR", "active": True},
            {"document_type": "LETA", "document_class": "MHR", "active": True},
            {"document_type": "MAID", "document_class": "MHR", "active": True},
            {"document_type": "MAIL", "document_class": "MHR", "active": True},
            {"document_type": "MARR", "document_class": "MHR", "active": True},
            {"document_type": "MEM", "document_class": "MHR", "active": True},
            {"document_type": "MHR_MISC", "document_class": "MHR", "active": True},
            {"document_type": "MHSP", "document_class": "MHR", "active": True},
            {"document_type": "NAMV", "document_class": "MHR", "active": True},
            {"document_type": "NCAN", "document_class": "MHR", "active": True},
            {"document_type": "NCON", "document_class": "MHR", "active": True},
            {"document_type": "NPUB", "document_class": "MHR", "active": True},
            {"document_type": "NRED", "document_class": "MHR", "active": True},
            {"document_type": "PRE", "document_class": "MHR", "active": True},
            {"document_type": "PUBA", "document_class": "MHR", "active": True},
            {"document_type": "REBU", "document_class": "MHR", "active": True},
            {"document_type": "REG_101", "document_class": "MHR", "active": True},
            {"document_type": "REG_102", "document_class": "MHR", "active": True},
            {"document_type": "REG_103", "document_class": "MHR", "active": True},
            {"document_type": "REGC", "document_class": "MHR", "active": True},
            {"document_type": "REIV", "document_class": "MHR", "active": True},
            {"document_type": "REPV", "document_class": "MHR", "active": True},
            {"document_type": "REST", "document_class": "MHR", "active": True},
            {"document_type": "STAT", "document_class": "MHR", "active": True},
            {"document_type": "SZL", "document_class": "MHR", "active": True},
            {"document_type": "TAXN", "document_class": "MHR", "active": True},
            {"document_type": "TAXS", "document_class": "MHR", "active": True},
            {"document_type": "THAW", "document_class": "MHR", "active": True},
            {"document_type": "TRAN", "document_class": "MHR", "active": True},
            {"document_type": "VEST", "document_class": "MHR", "active": True},
            {"document_type": "WHAL", "document_class": "MHR", "active": True},
            {"document_type": "WILL", "document_class": "MHR", "active": True},
            {"document_type": "CONS", "document_class": "NR", "active": True},
            {"document_type": "CONT", "document_class": "NR", "active": True},
            {"document_type": "CORR", "document_class": "NR", "active": True},
            {"document_type": "NR_MISC", "document_class": "NR", "active": True},
            {"document_type": "ADMN", "document_class": "OTHER", "active": True},
            {"document_type": "BCGT", "document_class": "OTHER", "active": True},
            {"document_type": "FINC", "document_class": "OTHER", "active": True},
            {"document_type": "FINM", "document_class": "OTHER", "active": True},
            {"document_type": "RPTP", "document_class": "OTHER", "active": True},
            {"document_type": "CONT", "document_class": "PPR", "active": True},
            {"document_type": "CORR", "document_class": "PPR", "active": True},
            {"document_type": "CRTO", "document_class": "PPR", "active": True},
            {"document_type": "DAT", "document_class": "PPR", "active": True},
            {"document_type": "FINS", "document_class": "PPR", "active": True},
            {"document_type": "FNCH", "document_class": "PPR", "active": True},
            {"document_type": "HSR", "document_class": "PPR", "active": True},
            {"document_type": "LHS", "document_class": "PPR", "active": True},
            {"document_type": "MEM", "document_class": "PPR", "active": True},
            {"document_type": "PPR", "document_class": "PPR", "active": True},
            {"document_type": "PPRC", "document_class": "PPR", "active": True},
            {"document_type": "PPR_MISC", "document_class": "PPR", "active": True},
            {"document_type": "PPRS", "document_class": "PPR", "active": True},
            {"document_type": "PRE", "document_class": "PPR", "active": True},
            {"document_type": "RGS", "document_class": "PPR", "active": True},
            {"document_type": "RPL", "document_class": "PPR", "active": True},
            {"document_type": "ADDR", "document_class": "SOCIETY", "active": True},
            {"document_type": "AFDV", "document_class": "SOCIETY", "active": True},
            {"document_type": "AMAL", "document_class": "SOCIETY", "active": True},
            {"document_type": "AMLG", "document_class": "SOCIETY", "active": True},
            {"document_type": "ANNR", "document_class": "SOCIETY", "active": True},
            {"document_type": "APCO", "document_class": "SOCIETY", "active": True},
            {"document_type": "ASNU", "document_class": "SOCIETY", "active": True},
            {"document_type": "ATTN", "document_class": "SOCIETY", "active": True},
            {"document_type": "BYLT", "document_class": "SOCIETY", "active": True},
            {"document_type": "BYLW", "document_class": "SOCIETY", "active": True},
            {"document_type": "CERT", "document_class": "SOCIETY", "active": True},
            {"document_type": "CLW", "document_class": "SOCIETY", "active": True},
            {"document_type": "CNST", "document_class": "SOCIETY", "active": True},
            {"document_type": "CNTA", "document_class": "SOCIETY", "active": True},
            {"document_type": "CNTI", "document_class": "SOCIETY", "active": True},
            {"document_type": "CNVS", "document_class": "SOCIETY", "active": True},
            {"document_type": "CONT", "document_class": "SOCIETY", "active": True},
            {"document_type": "CORC", "document_class": "SOCIETY", "active": True},
            {"document_type": "CORR", "document_class": "SOCIETY", "active": True},
            {"document_type": "COSD", "document_class": "SOCIETY", "active": True},
            {"document_type": "CRTO", "document_class": "SOCIETY", "active": True},
            {"document_type": "DIRS", "document_class": "SOCIETY", "active": True},
            {"document_type": "DISD", "document_class": "SOCIETY", "active": True},
            {"document_type": "FILE", "document_class": "SOCIETY", "active": True},
            {"document_type": "FRMA", "document_class": "SOCIETY", "active": True},
            {"document_type": "LTR", "document_class": "SOCIETY", "active": True},
            {"document_type": "MNOR", "document_class": "SOCIETY", "active": True},
            {"document_type": "OTP", "document_class": "SOCIETY", "active": True},
            {"document_type": "PLNA", "document_class": "SOCIETY", "active": True},
            {"document_type": "REGN", "document_class": "SOCIETY", "active": True},
            {"document_type": "REGO", "document_class": "SOCIETY", "active": True},
            {"document_type": "RSLN", "document_class": "SOCIETY", "active": True},
            {"document_type": "RSRI", "document_class": "SOCIETY", "active": True},
            {"document_type": "SOCF", "document_class": "SOCIETY", "active": True},
            {"document_type": "SOC_MISC", "document_class": "SOCIETY", "active": True},
            {"document_type": "SUPP", "document_class": "SOCIETY", "active": True},
            {"document_type": "SYSR", "document_class": "SOCIETY", "active": True},
            {"document_type": "XP_MISC", "document_class": "XP", "active": False},
            {"document_type": "REG_103E", "document_class": "MHR", "active": True},
            {"document_type": "AMEND_PERMIT", "document_class": "MHR", "active": True},
            {"document_type": "CANCEL_PERMIT", "document_class": "MHR", "active": True},
            {"document_type": "REREGISTER_C", "document_class": "MHR", "active": True},
            {"document_type": "MEAM", "document_class": "MHR", "active": False},
            {"document_type": "CLW", "document_class": "MHR", "active": False},
            {"document_type": "COMP", "document_class": "MHR", "active": False},
            {"document_type": "CONS", "document_class": "CORP", "active": True},
            {"document_type": "PART", "document_class": "CORP", "active": True},
            {"document_type": "NWP", "document_class": "CORP", "active": True},
            {"document_type": "BYLW", "document_class": "CORP", "active": True},
            {"document_type": "COFI", "document_class": "CORP", "active": True},
            {"document_type": "CRT", "document_class": "CORP", "active": True},
            {"document_type": "FINM", "document_class": "CORP", "active": True},
            {"document_type": "COPN", "document_class": "CORP", "active": True},
            {"document_type": "PRE", "document_class": "CORP", "active": True},
        ],
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document_types', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_class', postgresql.ENUM('COOP', 'CORP', 'FIRM', 'MHR', 'NR', 'OTHER', 'PPR', 'SOCIETY', 'XP', 'LP_LLP', 'DELETED', name='documentclass'), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('document_types_document_class_fkey', 'document_classes', ['document_class'], ['document_class'])

    with op.batch_alter_table('document_type_classes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_document_type_classes_document_type'))
        batch_op.drop_index(batch_op.f('ix_document_type_classes_document_class'))

    op.drop_table('document_type_classes')
    # ### end Alembic commands ###
