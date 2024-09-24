import type { DocumentInfoIF, DocumentStateIF } from '~/interfaces/document-types-interface'

export const useBcrosDocuments = defineStore('bcros/documents', () => {

  // Function to return default values
  const getDefaultState = (): DocumentStateIF => ({
    // Document Search
    searchResultCount: 0,
    searchDocumentId: '',
    searchDocuments: '',
    searchEntityId: '',
    searchDocumentClass: '',
    searchDocumentType: '',
    searchDateRange: { start: null, end: null },
    pageNumber: 0,

    // Document Meta
    consumerIdentifier: '',
    noIdCheckbox: false,
    noDocIdCheckbox: false,
    documentClass: '',
    documentType: '',
    consumerFilingDate: '',
    documentList: [],

    // Validations
    validateIndex: false,
    isLoading: false,
    
    // Document Review
    displayDocumentReview: false,
    documentInfoRO: null as DocumentInfoIF,
    documentSearchResults: [],
    documentRecord: null,

    // Document Editing
    isEditing: false
  })

  // Initial state
  const state = reactive(getDefaultState())

  // Reset state function
  const resetStore = () => {
    Object.assign(state, getDefaultState())
  }

  return {
    ...toRefs(state),
    resetStore, // Expose the reset function
  }
})