import type { AxiosError } from 'axios'
import type {
  ApiResponseIF,
  ApiResponseOrError,
  DocumentRequestIF,
  RequestDataIF
} from '~/interfaces/request-interfaces'

const config = useRuntimeConfig()
const baseURL = config.public.documentsApiURL
const docApiKey = config.public.documentsApiKey

/**
 * Sends a GET request to fetch a document from the specified API endpoint.
 *
 * @param params - The parameters for the document request, including document class, type, and consumer information.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function getDocuments(params: DocumentRequestIF): Promise<ApiResponseOrError> {
  const options = {
    method: 'GET',
    headers: { 'x-apikey': `${docApiKey}` }
  }

  const {
    pageNumber,
    consumerDocumentId,
    documentClass,
    documentType,
    consumerIdentifier,
    queryStartDate,
    queryEndDate
  } = params

  // Construct query parameters
  const queryParams = new URLSearchParams()
  if (pageNumber) queryParams.append('pageNumber', pageNumber.toString())
  if (consumerDocumentId) queryParams.append('consumerDocumentId', consumerDocumentId)
  if (consumerIdentifier) queryParams.append('consumerIdentifier', consumerIdentifier)
  if (documentType) queryParams.append('documentType', documentType)
  if (queryStartDate) queryParams.append('queryStartDate', queryStartDate)
  if (queryEndDate) queryParams.append('queryEndDate', queryEndDate)

  // Build the full URL
  const url = `${baseURL}/searches/${documentClass}?${queryParams.toString()}`

  try {
    const response = await useBcrosFetch<ApiResponseIF>(url, options)
    return {
      data: response.data,
      status: response.status
    }
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a POST request to upload a document to the specified API endpoint.
 *
 * @param params - The parameters for the document request, including document class, type, and optional consumer
 * information.
 * @param document - The document data to be sent in the request body.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function postDocument(params: DocumentRequestIF, document: RequestDataIF)
  : Promise<ApiResponseOrError> {
  const options = {
    method: 'POST',
    headers: { 'x-apikey': `${docApiKey}` },
    body: document
  }

  const {
    consumerDocumentId,
    documentClass,
    documentType,
    consumerFilename,
    consumerIdentifier,
    consumerFilingDate,
    description
  } = params

  // Construct query parameters
  const queryParams = new URLSearchParams()
  if (consumerDocumentId) queryParams.append('consumerDocumentId', consumerDocumentId)
  if (consumerFilename) queryParams.append('consumerFilename', consumerFilename)
  if (consumerIdentifier) queryParams.append('consumerIdentifier', consumerIdentifier)
  if (consumerFilingDate) queryParams.append('consumerFilingDate', consumerFilingDate)
  if (description) queryParams.append('description', description)


  // Build the full URL
  const url = `${baseURL}/documents/${documentClass}/${documentType}?${queryParams.toString()}`

  try {
    const response = await useBcrosFetch<ApiResponseIF>(url, options)
    return {
      data: response.data,
      status: response.status
    }
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a PUT request to update a document to the specified API endpoint.
 *
 * @param params - The parameters for the document request, including document class, type, and optional consumer
 * information.
 * @param document - The document data to be sent in the request body.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function updateDocument(params: DocumentRequestIF, document: RequestDataIF)
  : Promise<ApiResponseOrError> {
  const options = {
    method: 'PUT',
    headers: { 'x-apikey': `${docApiKey}` },
    body: document
  }

  const {
    consumerFilename,
    documentServiceId
  } = params

  // Construct query parameters
  const queryParams = new URLSearchParams()
  if (consumerFilename) queryParams.append('consumerFilename', consumerFilename)

  // Build the full URL
  const url = `${baseURL}/documents/${documentServiceId}?${queryParams.toString()}`

  try {
    await useBcrosFetch<ApiResponseIF>(url, options).then((response) => {
      return {
        data: response.data,
        status: response.status
      }
    })
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a Patch request to update a document record to the specified API endpoint.
 *
 * @param params - The parameters for the document request, including document class, type, and optional consumer
 * information.
 * @param document - The document data to be sent in the request body.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function updateDocumentRecord(params: DocumentRequestIF)
  : Promise<ApiResponseOrError> {
  const {
    documentServiceId,
    consumerDocumentId,
    consumerFilename,
    consumerIdentifier,
    consumerFilingDate,
    description
  } = params

  const options = {
    method: 'PATCH',
    headers: { 'x-apikey': `${docApiKey}` },
    body: {
      consumerDocumentId,
      consumerIdentifier,
      consumerFilename,
      consumerFilingDate,
      description
    }
  }

  // Build the full URL
  const url = `${baseURL}/documents/${documentServiceId}`

  try {
    await useBcrosFetch<ApiResponseIF>(url, options).then((response) => {
      return {
        data: response.data,
        status: response.status
      }
    })
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a POST request to upload a document to the specified API endpoint.
 *
 * @param params - The parameters for the document scanning data request.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function createScanningRecord(params: DocumentRequestIF)
  : Promise<ApiResponseOrError> {
  const {
    documentClass,
    consumerDocumentId,
    scanningDetails
  } = params

  const options = {
    method: 'POST',
    headers: { 'x-apikey': `${docApiKey}` },
    body: scanningDetails
  }

  // Build the full URL
  const url = `${baseURL}/scanning/${documentClass}/${consumerDocumentId}`

  try {
    await useBcrosFetch<ApiResponseIF>(url, options).then((response) => {
      return {
        data: response.data,
        status: response.status
      }
    })
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a PATCH request to upload a document to the specified API endpoint.
 *
 * @param params - The parameters for the document scanning data request.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function updateScanningRecord(params: DocumentRequestIF)
  : Promise<ApiResponseOrError> {
  const {
    documentClass,
    consumerDocumentId,
    scanningDetails
  } = params

  const options = {
    method: 'PATCH',
    headers: { 'x-apikey': `${docApiKey}` },
    body: scanningDetails
  }

  // Build the full URL
  const url = `${baseURL}/scanning/${documentClass}/${consumerDocumentId}`

  try {
    const response = await useBcrosFetch<ApiResponseIF>(url, options)
    return {
      data: response.data,
      status: response.status,
      statusCode: response.error?.value.statusCode
    }
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a GET request to retrieve a document record by its consumerDocumentId.
 *
 * @param consumerDocumentId - The unique identifier for the document to be retrieved.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function getDocumentRecord(consumerDocumentId: string): Promise<ApiResponseOrError> {
  const options = {
    method: 'GET',
    headers: { 'x-apikey': `${docApiKey}` }
  }

  // Build the full URL
  const url = `${baseURL}/documents/verify/${consumerDocumentId}`

  try {
    const response = await useBcrosFetch<ApiResponseIF>(url, options)
    return {
      data: response.data,
      status: response.status
    }
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a GET request to retrieve a document url by its docServiceId.
 *
 * @param documentClass - The document class to be retrieved.
 * @param docServiceId - The unique identifier for the document to be retrieved.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function getDocumentUrl(documentClass: string, docServiceId: string): Promise<ApiResponseOrError> {
  const options = {
    method: 'GET',
    headers: { 'x-apikey': `${docApiKey}` }
  }

  // Construct query parameters
  const queryParams = new URLSearchParams()
  if (docServiceId) queryParams.append('documentServiceId', docServiceId)

  // Build the full URL
  const url = `${baseURL}/searches/${documentClass}?${queryParams.toString()}`

  try {
    const response = await useBcrosFetch<ApiResponseIF>(url, options)
    return {
      data: response.data,
      status: response.status
    }
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a GET request to retrieve a document record report by its consumerDocumentId.
 *
 * @param consumerDocumentId - The unique identifier for the document to be retrieved.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function getDocumentRecordReport(consumerDocumentId: string): Promise<ApiResponseOrError> {
  const options = {
    method: 'GET',
    headers: { 'x-apikey': `${docApiKey}` }
  }

  // Build the full URL
  const url = `${baseURL}/reports/document-records/${consumerDocumentId}`

  try {
    const response = await useBcrosFetch<ApiResponseIF>(url, options)
    saveBlob(response.data.value, `${consumerDocumentId}.pdf`)
    return {
      data: response.data,
      status: response.status
    }
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}

/**
 * Sends a GET request to retrieve a document scanning record by its consumerDocumentId.
 *
 * @param documentClass - The class of the document to be retrieved.
 * @param documentId - The unique identifier for the document to be retrieved.
 * @returns A promise that resolves to either an ApiResponseIF on success or an ApiErrorIF on failure.
 */
export async function getScanningRecord(documentClass: string, documentId: string): Promise<ApiResponseOrError> {
  const options = {
    method: 'GET',
    headers: { 'x-apikey': `${docApiKey}` }
  }

  // Build the full URL
    const url = `${baseURL}/scanning/${documentClass}/${documentId}`

  try {
    const response = await useBcrosFetch<ApiResponseIF>(url, options)
    return {
      data: response.data,
      status: response.status
    }
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      message: axiosError.message,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
    }
  }
}