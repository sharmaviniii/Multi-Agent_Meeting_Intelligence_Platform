import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30_000,
});

export type RequestOptions = {
  signal?: AbortSignal;
};

export async function getJson<TResponse>(url: string, options: RequestOptions = {}) {
  const response = await apiClient.get<TResponse>(url, {
    signal: options.signal,
  });

  return response.data;
}

export async function postJson<TResponse, TBody>(
  url: string,
  body: TBody,
  options: RequestOptions = {},
) {
  const response = await apiClient.post<TResponse>(url, body, {
    signal: options.signal,
  });

  return response.data;
}
