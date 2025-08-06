import type { AxiosError } from 'axios'
import type {
  ApiResponseOrError,
  RequestDataIF
} from '~/interfaces/request-interfaces'

/**
 * Converts a document to PDF by sending a POST request to the PDF conversion API.
 *
 * @param document - The document data to be converted, conforming to RequestDataIF.
 * @returns A promise that resolves to a PDF blob on success, or an error object with message, status, and statusText on failure.
 */
export async function pdfConversion(document: RequestDataIF)
  : Promise<ApiResponseOrError> {
  const config = useRuntimeConfig()
  const baseURL = config.public.documentsApiURL
  const docApiKey = config.public.documentsApiKey

  const options = {
    method: 'POST',
    headers: {
      'Accept': 'application/pdf',
      'x-apikey': `${docApiKey}`,
      'Account-Id': '3040',
      'Authorization': `Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJreXk4aGdkTzVsM3Nwb3k3RnlPWU4wN1ZIWnhYT1hmYUxiV2tuaTZIZHhFIn0.eyJleHAiOjE3NTQ1MDkxNzIsImlhdCI6MTc1NDQ5MTE3MiwiYXV0aF90aW1lIjoxNzU0NDkxMTU0LCJqdGkiOiJvbnJ0YWM6MDAzYjJiMzEtMjgyYS00OTBiLWFkYWQtZTliOGFkZDdjODEzIiwiaXNzIjoiaHR0cHM6Ly9kZXYubG9naW5wcm94eS5nb3YuYmMuY2EvYXV0aC9yZWFsbXMvYmNyZWdpc3RyeSIsImF1ZCI6WyJwcHItc2VydmljZXMiLCJhY2NvdW50LXNlcnZpY2VzIiwiYWNjb3VudCJdLCJzdWIiOiJhY2IwZGRmZS1hNjkxLTRkNDQtYmE0Ny1iMjYwZDM5MGE4OTYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwcHItd2ViIiwic2lkIjoiNDE2MmViN2UtOWE4YS00MWZjLWFkNDAtZTBjZjE2Nzg5YmM0IiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm1hbmFnZV9idXNpbmVzcyIsIm5hbWVzX2FwcHJvdmVyIiwibmFtZXNfdmlld2VyIiwiYWRtaW5fZWRpdCIsImFkbWluX3ZpZXciLCJtYW5hZ2VfYWNjb3VudHMiLCJzZWFyY2giLCJ2aWV3Iiwidmlld19zdGFmZl9kYXNoYm9hcmQiLCJtaHJfc3RhZmYiLCJjcmVhdGVfY3JlZGl0cyIsIm9mZmxpbmVfYWNjZXNzIiwic3VzcGVuZF9hY2NvdW50cyIsInVtYV9hdXRob3JpemF0aW9uIiwibWFrZV9wYXltZW50IiwibWhyX3RyYW5zZmVyX3NhbGUiLCJkZWZhdWx0LXJvbGVzLWJjcmVnaXN0cnkiLCJuYW1lc19lZGl0b3IiLCJ2aWV3X2FjY291bnRzIiwibWhyX3BheW1lbnQiLCJlZGl0IiwibWhyX3JlZ2lzdGVyIiwic3RhZmYiLCJtaHJfdHJhbnNwb3J0IiwibWhyX3RyYW5zZmVyX2RlYXRoIiwicHByX3N0YWZmIiwicHByIiwibWhyIiwiYWNjb3VudF9ob2xkZXIiLCJtaHJfZXhlbXB0aW9uX25vbl9yZXMiLCJtaHJfZXhlbXB0aW9uX3JlcyIsIm5hbWVzX21hbmFnZXIiXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImZpcnN0bmFtZSI6IkNhbWVyb24iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInJvbGVzIjpbIm1hbmFnZV9idXNpbmVzcyIsIm5hbWVzX2FwcHJvdmVyIiwibmFtZXNfdmlld2VyIiwiYWRtaW5fZWRpdCIsImFkbWluX3ZpZXciLCJtYW5hZ2VfYWNjb3VudHMiLCJzZWFyY2giLCJ2aWV3Iiwidmlld19zdGFmZl9kYXNoYm9hcmQiLCJtaHJfc3RhZmYiLCJjcmVhdGVfY3JlZGl0cyIsIm9mZmxpbmVfYWNjZXNzIiwic3VzcGVuZF9hY2NvdW50cyIsInVtYV9hdXRob3JpemF0aW9uIiwibWFrZV9wYXltZW50IiwibWhyX3RyYW5zZmVyX3NhbGUiLCJkZWZhdWx0LXJvbGVzLWJjcmVnaXN0cnkiLCJuYW1lc19lZGl0b3IiLCJ2aWV3X2FjY291bnRzIiwibWhyX3BheW1lbnQiLCJlZGl0IiwibWhyX3JlZ2lzdGVyIiwic3RhZmYiLCJtaHJfdHJhbnNwb3J0IiwibWhyX3RyYW5zZmVyX2RlYXRoIiwicHByX3N0YWZmIiwicHByIiwibWhyIiwiYWNjb3VudF9ob2xkZXIiLCJtaHJfZXhlbXB0aW9uX25vbl9yZXMiLCJtaHJfZXhlbXB0aW9uX3JlcyIsIm5hbWVzX21hbmFnZXIiXSwibmFtZSI6IkNhbWVyb24gQm93bGVyIiwiaWRwX3VzZXJpZCI6IkNEMzZDQ0JFN0U1MjRFRDg5N0M1RDIzODA4MzA1MjRCIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiY2Jvd2xlckBpZGlyIiwiZ2l2ZW5fbmFtZSI6IkNhbWVyb24iLCJmYW1pbHlfbmFtZSI6IkJvd2xlciIsImxvZ2luU291cmNlIjoiSURJUiIsImVtYWlsIjoiY2FtZXJvbi5ib3dsZXJAZ292LmJjLmNhIiwibGFzdG5hbWUiOiJCb3dsZXIiLCJ1c2VybmFtZSI6ImNib3dsZXJAaWRpciJ9.Tyotd4R66qSudLkwWZxiAB4BUMxuJVREyF6dpkUT07KJc22xIJT_FOUCHcB-Yj8KN4u-p9dxrZOZxC13dyb_nT5kc5RgAvWXMxTz8hwGjsIFfjblUhL-gtR1V_1T_VugauIN0hs0iwWbViEBvJKh5mPu0sdbp0n1pS456SA9s-sieDxRWvKnZY0kjrTNe6TH56E35yIcDnIIAjyQah0u7-wqc7wnEsHCvT7uOLa8aZrVuOm_0gWlcf4vA2RnpgKg4bV_K_OvUBwhi8X1f9dlU3z8cgmgb3ChV_WAaQ9siifkN2El5inQ53mpGMc_K29tjYuCY-KWXFJau8sKaY3r3g`
    },
    body: document
  }

  const url = `${baseURL}/pdf-conversions`
  try {
    const response = await $fetch(url, options)
    if (!(response instanceof Blob)) {
      throw { message: 'No PDF blob returned', status: 'error' }
    }
    return response
  } catch (error) {
    return {
      message: (error as Error).message,
      status: (error as AxiosError)?.response?.status || 'error',
      statusText: 'Error occurred while converting document to PDF'
    }
  }
}
