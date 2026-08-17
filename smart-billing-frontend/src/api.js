import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
});

export const getProducts = () => api.get('/products');
export const getCustomers = () => api.get('/customers');
export const createInvoice = (data) => api.post('/invoices', data);

export const importProducts = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/products/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const exportProducts = () => api.get('/products/export', { responseType: 'blob' });
export const exportInvoices = () => api.get('/invoices/export', { responseType: 'blob' });

export const downloadFile = (blobData, filename) => {
  const url = window.URL.createObjectURL(new Blob([blobData]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};