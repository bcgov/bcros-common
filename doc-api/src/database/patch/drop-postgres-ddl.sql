-- Already connected to the docs database.
DROP FUNCTION public.get_default_doc_id();

DROP SEQUENCE service_doc_id_seq;
DROP SEQUENCE document_id_seq;
DROP SEQUENCE request_id_seq;
DROP SEQUENCE user_id_seq;

DROP INDEX ix_documents_type;
DROP INDEX ix_documents_add_ts;
DROP INDEX ix_documents_doc_id;
DROP INDEX ix_documents_doc_id;
DROP INDEX ix_documents_con_doc_id;
DROP INDEX ix_requests_request_ts;
DROP INDEX ix_requests_account_id;
DROP INDEX ix_requests_document_id;
DROP INDEX ix_users_account_id;
DROP INDEX ix_users_username;

DROP TABLE public.documents;
DROP TABLE public.document_requests;
DROP TABLE public.users;
DROP TABLE public.document_types;
DROP TABLE public.request_types;

DROP TYPE public.document_type;
DROP TYPE public.request_type;
-- Drop end
