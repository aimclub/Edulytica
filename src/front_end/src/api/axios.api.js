// English comments per project convention
import axios from 'axios';

// Base URL for all requests
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const $api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// No interceptors here! Only pure instance
export default $api;
