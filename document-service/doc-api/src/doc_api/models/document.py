# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module holds data for individual documents."""

from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.sql import text
from doc_api.exceptions import DatabaseException
from doc_api.models import utils as model_utils
from doc_api.utils.logging import logger

from .db import db
from .type_tables import DocumentTypes


QUERY_KEYS = """
select nextval('document_id_seq') AS doc_id,
       get_service_doc_id() AS service_doc_id,
       get_document_number() AS consumer_doc_id
"""
QUERY_KEYS_NO_DOC_ID = """
select nextval('document_id_seq') AS doc_id,
       get_service_doc_id() AS service_doc_id
"""


class Document(db.Model):
    """This class manages all of the document service document information."""

    __tablename__ = 'documents'

    id = db.mapped_column('id', db.Integer, primary_key=True)
    document_service_id = db.mapped_column('document_service_id', db.String(20), nullable=False, unique=True)
    add_ts = db.mapped_column('add_ts', db.DateTime, nullable=False, index=True)
    consumer_document_id = db.mapped_column('consumer_document_id', db.String(20), nullable=False, index=True)
    consumer_identifier = db.mapped_column('consumer_identifier', db.String(20), nullable=True, index=True)
    consumer_filename = db.mapped_column('consumer_filename', db.String(1000), nullable=True)
    consumer_filing_date = db.mapped_column('consumer_filing_date', db.DateTime, nullable=True, index=True)
    scan_date = db.mapped_column('scan_date', db.DateTime, nullable=True)
    doc_storage_url = db.mapped_column('doc_storage_url', db.String(1000), nullable=True)

    # parent keys
    document_type = db.mapped_column('document_type', PG_ENUM(DocumentTypes, name='documenttype'),
                                     db.ForeignKey('document_types.document_type'), nullable=False)

    # Relationships
    doc_type = db.relationship('DocumentType', foreign_keys=[document_type],
                               back_populates='document', cascade='all, delete', uselist=False)
    doc_requests = db.relationship('DocumentRequest', order_by='asc(DocumentRequest.id)', back_populates='document')

    @property
    def json(self) -> dict:
        """Return the document as a json object."""
        document = {
            'documentServiceId': self.document_service_id,
            'createDateTime': model_utils.format_ts(self.add_ts),
            'consumerDocumentId': self.consumer_document_id,
            'consumerFilename': self.consumer_filename if self.consumer_filename else '',
            'consumerIdentifier': self.consumer_identifier if self.consumer_identifier else '',
            'documentType': self.document_type,
            'documentTypeDescription': self.doc_type.document_type_desc if self.doc_type else '',
            'documentClass': self.doc_type.document_class if self.doc_type else '',
            'documentURL': self.doc_storage_url if self.doc_storage_url else ''
        }
        if self.consumer_filing_date:
            document['consumerFilingDateTime'] = model_utils.format_ts(self.consumer_filing_date)
        if self.scan_date:
            document['consumerScanDateTime'] = model_utils.format_ts(self.scan_date)
        return document

    @classmethod
    def find_by_id(cls, pkey: int = None):
        """Return a document object by primary key."""
        document = None
        if pkey:
            try:
                document = db.session.query(Document).filter(Document.id == pkey).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                logger.error('Document.find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception) from db_exception
        return document

    @classmethod
    def find_by_doc_service_id(cls, doc_service_id: str):
        """Return a document object by document service ID."""
        documents = None
        if doc_service_id:
            try:
                documents = db.session.query(Document) \
                    .filter(Document.document_service_id == doc_service_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                logger.error('Document.find_by_doc_service_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception) from db_exception
        return documents

    @classmethod
    def find_by_document_id(cls, doc_id: str):
        """Return a list of document objects by consumer document id/number."""
        documents = None
        if doc_id:
            try:
                documents = db.session.query(Document) \
                    .filter(Document.consumer_document_id == doc_id).order_by(Document.id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                logger.error('Document.find_by_document_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception) from db_exception
        return documents

    @classmethod
    def find_by_consumer_id(cls, consumer_id: str, doc_type: str = None):
        """Return a list of document objects by consumer document id/number and optional document type."""
        documents = None
        if consumer_id:
            try:
                if doc_type:
                    logger.info(f'querying by consumer ID {consumer_id} and doc type {doc_type}')
                    documents = db.session.query(Document) \
                        .filter(and_(Document.consumer_identifier == consumer_id,
                                     Document.document_type == doc_type)) \
                        .order_by(Document.consumer_document_id).all()
                else:
                    documents = db.session.query(Document) \
                        .filter(Document.consumer_identifier == consumer_id) \
                        .order_by(Document.consumer_document_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                logger.error('Document.find_by_consumer_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception) from db_exception
        return documents

    def get_generated_values(self):
        """Get db generated identifiers that are in more than one table or required up front.

        Get document id, document service id, and optionally consumer document id.
        """
        query_text = QUERY_KEYS
        if self.consumer_document_id:
            query_text = QUERY_KEYS_NO_DOC_ID
        query = text(query_text)
        result = db.session.execute(query)
        row = result.first()
        self.id = int(row[0])
        self.document_service_id = str(row[1])
        if not self.consumer_document_id:
            self.consumer_document_id = str(row[2])

    def save(self):
        """Store the Document into the local cache."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def create_from_json(doc_json: dict, doc_type: str):
        """Create a new document object from a new save document request."""
        doc = Document(add_ts=model_utils.now_ts(),
                       document_type=doc_type)
        if doc_json.get('consumerDocumentId'):
            doc.consumer_document_id = doc_json.get('consumerDocumentId')
        if doc_json.get('consumerFilename'):
            doc.consumer_filename = doc_json.get('consumerFilename')
        if doc_json.get('consumerIdentifier'):
            doc.consumer_identifier = doc_json.get('consumerIdentifier')
        if doc_json.get('consumerFilingDateTime'):
            doc.consumer_filing_date = model_utils.ts_from_iso_date_noon(doc_json['consumerFilingDateTime'])
        elif doc_json.get('consumerFilingDate'):
            doc.consumer_filing_date = model_utils.ts_from_iso_date_noon(doc_json['consumerFilingDate'])
        if doc_json.get('consumerScanDateTime'):
            doc.scan_date = model_utils.ts_from_iso_date_noon(doc_json['consumerScanDateTime'])
        elif doc_json.get('consumerScanDate'):
            doc.scan_date = model_utils.ts_from_iso_date_noon(doc_json['consumerScanDate'])
        doc.get_generated_values()
        return doc
