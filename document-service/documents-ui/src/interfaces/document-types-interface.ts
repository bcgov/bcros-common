import type { DocumentRequestIF } from '~/interfaces/request-interfaces'

export interface DocumentStateIF {
  // Document Search
  searchDocumentId: string
  searchEntityId: string
  searchDocumentClass: string
  searchDocumentType: string
  searchDateRange: {
    start: Date | null
    end: Date | null
  }

  // Document Meta
  consumerIdentifier: string
  noIdCheckbox: boolean
  noDocIdCheckbox: boolean
  documentClass: string
  documentType: string
  consumerFilingDate: string
  documentList: Array<any>

  // Validations
  validateIndex: boolean
  isLoading: boolean
  validateDocumentSearch: boolean

  // Document Review
  displayDocumentReview: boolean
  documentInfoRO: DocumentInfoIF | null
  documentSearchResults: DocumentRequestIF[]
  documentRecord: DocumentInfoIF | null
}

export interface DocumentDetailIF {
  type: string
  description: string
  productCode: string
}

export interface DocumentClassIF {
  class: string
  description: string
  prefixes: Array<string>
  documents: Array<DocumentDetailIF>
}

export interface DocumentInfoIF {
  consumerDocumentId: string
  consumerFilename: string
  consumerFilingDateTime: string
  consumerIdentifier: string
  createDateTime: string
  documentClass: string
  documentServiceId: string
  documentType: string
  documentTypeDescription?: string
  documentDescription: string
  documentURL: string
  filenames: Array<string>
  consumerFilenames?: Array<string>
  documentUrls?: Array<string>
  documentList?: Array<any>

  // Scanning properties
  scanDateTime: string
  accessionNumber: string
  batchId: string
  pageCount: number
  author: string
}