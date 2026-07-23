import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
});

export const getProducts = () => api.get('/products');
export const getCustomers = () => api.get('/customers');
export const createInvoice = (data) => api.post('/invoices', data);