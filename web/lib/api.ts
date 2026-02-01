import { headers } from "next/headers";

const DEFAULT_BACKEND_HOST =
  process.env.BACKEND_HOST ??
  process.env.NEXT_PUBLIC_BACKEND_HOST ??
  "127.0.0.1";
const DEFAULT_BACKEND_PORT =
  process.env.BACKEND_PORT ??
  process.env.NEXT_PUBLIC_BACKEND_PORT ??
  "8000";
const API_PATH = "/api/lets-learn/";
const DEFAULT_API_ROOT =
  process.env.API_ROOT ??
  process.env.NEXT_PUBLIC_API_ROOT ??
  `http://${DEFAULT_BACKEND_HOST}:${DEFAULT_BACKEND_PORT}${API_PATH}`;

export const getRequestHostname = async () => {
  const requestHeaders = await headers();
  const forwardedHost = requestHeaders.get("x-forwarded-host");
  const host = forwardedHost ?? requestHeaders.get("host") ?? "";
  const hostname = host.split(":")[0];

  return hostname || DEFAULT_BACKEND_HOST;
};

export const getApiRoot = () => {
  return DEFAULT_API_ROOT;
};

export const normalizeMediaUrl = (
  url: string | null | undefined,
  hostname: string,
  port: string = DEFAULT_BACKEND_PORT,
) => {
  if (!url) {
    return null;
  }

  try {
    const baseUrl = `http://${hostname}:${port}`;
    const parsedUrl = new URL(url, baseUrl);

    if (
      parsedUrl.hostname === "localhost" ||
      parsedUrl.hostname === "127.0.0.1"
    ) {
      parsedUrl.hostname = hostname;
      parsedUrl.port = port;
      parsedUrl.protocol = "http:";
    }

    return parsedUrl.toString();
  } catch {
    return url;
  }
};
