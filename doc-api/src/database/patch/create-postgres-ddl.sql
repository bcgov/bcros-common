-- Already connected to the docs database.
CREATE SEQUENCE service_doc_id_seq INCREMENT 1 START 100000000;
CREATE OR REPLACE FUNCTION public.get_default_doc_id()
RETURNS VARCHAR
LANGUAGE plpgsql
AS
$$
  BEGIN
    RETURN 'DS' || trim(to_char(nextval('service_doc_id_seq'), '000000000'));
  END
; 
$$;


CREATE TYPE public.request_type AS ENUM ('ADD', 'GET', 'REPLACE', 'UPDATE_ID');
CREATE TABLE public.request_types (
  request_type public.request_type PRIMARY KEY,
  request_type_desc VARCHAR (100) NOT NULL
);
INSERT INTO request_types(request_type, request_type_desc) VALUES
('ADD', 'Add a new document.'),
('GET', 'Fetch an existing document.'),
('REPLACE', 'Staff only replace existing document uploaded in error.'),
('UPDATE_ID', 'Add/replace a consumer id associated with a document.')
;
CREATE TYPE public.document_type 
    AS ENUM ('SPGP_DISS',
             'SPGP_ADDR',
             'SPGP_PARTNER',
             'SPGP_PROP_NAME',
             'SPGP_BUS_NAME',
             'SPGP_NOB',
             'SPGP_GEN_CORR',
             'SPGP_CONV',
             'SPGP_AMALG',
             'SPGP_MISC',
             'LP_REG790',
             'LP_REG791',
             'LP_REG_CERT',
             'LP_AM_CERT',
             'LP_REG_OFF',
             'LP_NOC_GP',
             'LP_DISS',
             'LP_EP_PROOF',
             'LP_PARTNER_PROOF',
             'LP_MISC',
             'COOP_AGM',
             'COOP_CORRECT',
             'COOP_REFUND',
             'COOP_MISC',
             'LLP_FORM1',
             'LLP_FORM2',
             'LLP_FORM3',
             'LLP_FORM4',
             'LLP_FORM5',
             'LLP_FORM6',
             'LLP_FORM7',
             'LLP_FORM8',
             'LLP_DISS',
             'LLP_MISC',
             'SOC_AR',
             'SOC_RESTORE',
             'SOC_CORRECT',
             'SOC_DEL_DIR',
             'SOC_ADDRESS',
             'SOC_DIRECTOR',
             'SOC_AMALG',
             'SOC_CONTI',
             'SOC_REFUND',
             'SOC_RECORD',
             'SOC_MISC',
             'CORP_FORM2',
             'CORP_FORM7',
             'CORP_FORM8',
             'CORP_FORM9',
             'CORP_FORM12',
             'CORP_FORM15',
             'CORP_FORM18',
             'CORP_FORM19',
             'CORP_FORM20',
             'CORP_FORM21',
             'CORP_FORM22',
             'CORP_FORM23',
             'CORP_FORM24',
             'CORP_FORM25',
             'CORP_FORM26',
             'CORP_FORM27',
             'CORP_FORM28',
             'CORP_FORM29',
             'CORP_FORM30',
             'CORP_FORM45',
             'CORP_FORM47',
             'CORP_FORM52',
             'CORP_FORM54',
             'CORP_EP_CERT_HOME',
             'CORP_MISC',
             'EP_FORM20',
             'EP_FORM29',
             'EP_FORM31',
             'EP_FORM33',
             'EP_FORM34',
             'EP_FORM36',
             'EP_FORM41',
             'EP_FORM44',
             'EP_MISC',
             'BC_FORM51',
             'BC_FORM53',
             'BC_MISC',
             'MHR_TRANSFER',
             'MHR_CORR',
             'MHR_AMEND',
             'MHR_LOCATION',
             'MHR_REG',
             'MHR_NOTICE',
             'MHR_NOTE',
             'MHR_EXEMPTION',
             'MHR_MISC'
);
             
CREATE TABLE public.document_types (
  document_type public.document_type PRIMARY KEY,
  document_type_desc VARCHAR (100) NOT NULL,
  product VARCHAR (20) NOT NULL,
  doc_id_required BOOLEAN NOT NULL DEFAULT FALSE
);
INSERT INTO document_types(document_type, document_type_desc, product, doc_id_required) VALUES
('MHR_TRANSFER', 'MHR Transfers', 'mhr', FALSE),
('MHR_CORR', 'MHR Corrections', 'mhr', FALSE),
('MHR_AMEND', 'MHR Amendments', 'mhr', FALSE),
('MHR_LOCATION', 'MHR Transport permits/location changes', 'mhr', FALSE),
('MHR_REG', 'MHR Registrations', 'mhr', FALSE),
('MHR_NOTICE', 'MHR Notices', 'mhr', FALSE),
('MHR_NOTE', 'MHR Notes', 'mhr', FALSE),
('MHR_EXEMPTION', 'MHR Exemptions', 'mhr', FALSE),
('MHR_MISC', 'MHR miscellaneous documents', 'mhr', FALSE),
('BC_FORM51', 'BC Notice of Alteration: from B.C. Unlimited Liability Company to B.C. Benefit Company', 'business', FALSE),
('BC_FORM53', 'BC Notice of Alteration: from a Benefit Company to B.C. Company', 'business', FALSE),
('BC_MISC', 'BC miscellaneous documents', 'business', FALSE),
('EP_FORM20', 'EP Notice of Withdrawal', 'business', FALSE),
('EP_FORM29', 'EP Limited Reinstatement', 'business', FALSE),
('EP_FORM31', 'EP Full Reinstatement Application', 'business', FALSE),
('EP_FORM33', 'EP (For LLC’s) - Registration Statement', 'business', FALSE),
('EP_FORM34', 'EP Notice of Amalgamation', 'business', FALSE),
('EP_FORM36', 'EP Change of Address', 'business', FALSE),
('EP_FORM41', 'EP Notice of Resignation of Attorney', 'business', FALSE),
('EP_FORM44', 'EP Notice of Change or Cancellation of Assumed Name', 'business', FALSE),
('EP_MISC', 'EP miscellaneous documents', 'business', FALSE),
('CORP_FORM2', 'CORP Notice of Change of Address', 'business', FALSE),
('CORP_FORM7', 'CORP All related to receivership. Appointment, change of address and ceasing to act as a receiver', 'business', FALSE),
('CORP_FORM8', 'CORP All related to receivership. Appointment, change of address and ceasing to act as a receiver', 'business', FALSE),
('CORP_FORM9', 'CORP All related to receivership. Appointment, change of address and ceasing to act as a receiver', 'business', FALSE),
('CORP_FORM12', 'CORP Special Act Corporation Conversion Application', 'business', FALSE),
('CORP_FORM15', 'CORP Application for Authorization for Amalgamation into a Foreign Jurisdiction', 'business', FALSE),
('CORP_FORM18', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM19', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM20', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM21', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM22', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM23', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM24', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM25', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM26', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM27', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM28', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM29', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM30', 'CORP Related to Liquidation', 'business', FALSE),
('CORP_FORM45', 'CORP Application for Authorization to Continue Out', 'business', FALSE),
('CORP_FORM47', 'CORP Application to Correct the Corporate Register', 'business', FALSE),
('CORP_FORM52', 'CORP Notice of Alteration: from B.C. Company to B.C. Benefit Company', 'business', FALSE),
('CORP_FORM54', 'CORP Application to Remove Oneself as Director', 'business', FALSE),
('CORP_EP_CERT_HOME', 'CORP Certificates from the Home Jurisdiction', 'business', FALSE),
('CORP_MISC', 'CORP miscellaneous documents', 'business', FALSE),
('SOC_AR', 'SOC annual report', 'business', FALSE),
('SOC_RESTORE', 'SOC limited/full restoration', 'business', FALSE),
('SOC_CORRECT', 'SOC correction', 'business', FALSE),
('SOC_DEL_DIR', 'SOC remove oneself as director', 'business', FALSE),
('SOC_ADDRESS', 'SOC change of address', 'business', FALSE),
('SOC_DIRECTOR', 'SOC change of director', 'business', FALSE),
('SOC_AMALG', 'SOC amalgamation', 'business', FALSE),
('SOC_CONTI', 'SOC continuation in', 'business', FALSE),
('SOC_REFUND', 'SOC refund letters', 'business', FALSE),
('SOC_RECORD', 'SOC appointment of a record keeper (if soc dissolved)', 'business', FALSE),
('SOC_MISC', 'SOC miscellaneous documents', 'business', FALSE),
('LLP_FORM1', 'LLP form 1', 'business', FALSE),
('LLP_FORM2', 'LLP form 2', 'business', FALSE),
('LLP_FORM3', 'LLP form 3', 'business', FALSE),
('LLP_FORM4', 'LLP form 4', 'business', FALSE),
('LLP_FORM5', 'LLP form 5', 'business', FALSE),
('LLP_FORM6', 'LLP form 6', 'business', FALSE),
('LLP_FORM7', 'LLP form 7', 'business', FALSE),
('LLP_FORM8', 'LLP form 8', 'business', FALSE),
('LLP_DISS', 'LLP letter of dissolution', 'business', FALSE),
('LLP_MISC', 'LLP any relevant correspondence or needed associated documents', 'business', FALSE),
('COOP_AGM', 'COOP AGM extensions (correspondence type in SOFI)', 'business', FALSE),
('COOP_CORRECT', 'COOP correction forms', 'business', FALSE),
('COOP_REFUND', 'COOP refund letters', 'business', FALSE),
('COOP_MISC', 'COOP miscellaneous documents', 'business', FALSE),
('SPGP_DISS', 'SP/GP Dissolution Due to Death', 'business', FALSE),
('SPGP_ADDR', 'SP/GP Change of Address', 'business', FALSE),
('SPGP_PARTNER', 'SP/GP Change of Partners of a General Partnership', 'business', FALSE),
('SPGP_PROP_NAME', 'SP/GP Change of Proprietor Name', 'business', FALSE),
('SPGP_BUS_NAME', 'SP/GP Change of Business Name', 'business', FALSE),
('SPGP_NOB', 'SP/GP Change in Nature of Business', 'business', FALSE),
('SPGP_GEN_CORR', 'SP/GP General Correspondence', 'business', FALSE),
('SPGP_CONV', 'SP/GP Conversions', 'business', FALSE),
('SPGP_AMALG', 'SP/GP Update Due to Amalgamation', 'business', FALSE),
('SPGP_MISC', 'SP/GP miscellaneous documents', 'business', FALSE),
('LP_REG790', 'LP Reg 790 for registrations, corrections or dissolution', 'business', FALSE),
('LP_REG791', 'LP Reg 791 for registrations, corrections or dissolution', 'business', FALSE),
('LP_REG_CERT', 'LP Certificate of registration', 'business', FALSE),
('LP_AM_CERT', 'LP Amended Certificate', 'business', FALSE),
('LP_REG_OFF', 'LP Notice of Registered Office / Amended Notice of Registered Office', 'business', FALSE),
('LP_NOC_GP', 'LP Notice of General Partners / Amended Notice of General Partners', 'business', FALSE),
('LP_DISS', 'LP Dissolution letters', 'business', FALSE),
('LP_EP_PROOF', 'LP Current Proof of Existence in the Home Jurisdiction for EPs', 'business', FALSE),
('LP_PARTNER_PROOF', 'LP letter confirming that the partnership still exists', 'business', FALSE),
('LP_MISC', 'LP miscellaneous documents', 'business', FALSE)
;

CREATE SEQUENCE user_id_seq INCREMENT 1 START 1;
CREATE TABLE public.users (
  id INTEGER PRIMARY KEY,
  creation_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  username VARCHAR(1000) NOT NULL,
  sub VARCHAR (36) NOT NULL,
  account_id VARCHAR (20) NULL,
  firstname VARCHAR (1000) NULL,
  lastname VARCHAR (1000) NULL,
  email VARCHAR (1000) NULL,
  iss VARCHAR (1024) NULL,
  idp_userid VARCHAR (256) NULL,
  login_source VARCHAR (200) NULL
);
CREATE INDEX ix_users_account_id ON public.users USING btree (account_id);
CREATE INDEX ix_users_username ON public.users USING btree (username);

CREATE SEQUENCE document_id_seq INCREMENT 1 START 100000;
CREATE TABLE public.documents (
  id INTEGER PRIMARY KEY,
  document_type public.document_type  NOT NULL,
  add_ts TIMESTAMP NOT NULL,
  doc_storage_url VARCHAR (1000) NOT NULL,
  document_service_id VARCHAR (20) NOT NULL,
  consumer_document_id VARCHAR (20) NULL,
  consumer_identifier VARCHAR (20) NULL,
  FOREIGN KEY (document_type)
      REFERENCES document_types (document_type)
);
CREATE INDEX ix_documents_add_ts ON public.documents USING btree (add_ts);
CREATE INDEX ix_documents_doc_id ON public.documents USING btree (document_service_id);
CREATE INDEX ix_documents_type ON public.documents USING btree (document_type);
CREATE INDEX ix_documents_con_doc_id ON public.documents USING btree (consumer_document_id);
CREATE INDEX ix_documents_con_id ON public.documents USING btree (consumer_identifier);

CREATE SEQUENCE request_id_seq INCREMENT 1 START 1;
CREATE TABLE public.document_requests (
  id INTEGER PRIMARY KEY,
  request_type public.request_type NOT NULL,
  request_ts TIMESTAMP NOT NULL,
  account_id VARCHAR (20) NOT NULL,
  username VARCHAR (1000) NULL,
  document_id INTEGER NULL,
  request_path VARCHAR (1000) NULL,
  status INTEGER NULL,
  status_message VARCHAR (4000) NULL,
  FOREIGN KEY (request_type)
      REFERENCES request_types (request_type),
  FOREIGN KEY (document_id)
      REFERENCES documents (id)
);
CREATE INDEX ix_requests_account_id ON public.document_requests USING btree (account_id);
CREATE INDEX ix_requests_request_ts ON public.document_requests USING btree (request_ts);
CREATE INDEX ix_requests_document_id ON public.document_requests USING btree (document_id);
-- Creat end
