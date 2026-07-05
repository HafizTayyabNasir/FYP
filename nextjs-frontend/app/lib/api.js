const API_BASE = '/api/v1';

export async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'API request failed');
    return data;
  } catch (error) {
    throw error;
  }
}

export { API_BASE };
