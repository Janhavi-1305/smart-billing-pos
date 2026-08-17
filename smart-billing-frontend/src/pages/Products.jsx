import { useEffect, useState, useRef } from 'react';
import { getProducts, importProducts, exportProducts, exportInvoices, downloadFile } from '../api';

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [importing, setImporting] = useState(false);
  const fileInputRef = useRef(null);

  const loadProducts = () => {
    setLoading(true);
    getProducts()
      .then((res) => setProducts(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setImporting(true);
    setImportResult(null);
    try {
      const res = await importProducts(file);
      setImportResult(res.data);
      loadProducts();
    } catch (err) {
      setImportResult({ error: err.response?.data?.detail || err.message });
    } finally {
      setImporting(false);
      fileInputRef.current.value = '';
    }
  };

  const handleExportProducts = async () => {
    const res = await exportProducts();
    downloadFile(res.data, 'products_export.xlsx');
  };

  const handleExportInvoices = async () => {
    const res = await exportInvoices();
    downloadFile(res.data, 'invoices_export.xlsx');
  };

  if (loading) return <p>Loading products...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>Products</h2>

      <div style={{ marginBottom: '15px', display: 'flex', gap: '10px', alignItems: 'center' }}>
        <button onClick={() => fileInputRef.current.click()} disabled={importing}>
          {importing ? 'Importing...' : 'Import from Excel'}
        </button>
        <input
          type="file"
          accept=".xlsx"
          ref={fileInputRef}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        <button onClick={handleExportProducts}>Export Products</button>
        <button onClick={handleExportInvoices}>Export Invoices</button>
      </div>

      {importResult && (
        <div style={{ marginBottom: '15px', padding: '10px', border: '1px solid #ccc', background: '#f9f9f9' }}>
          {importResult.error ? (
            <p style={{ color: 'red' }}>Error: {JSON.stringify(importResult.error)}</p>
          ) : (
            <>
              <p>Imported: {importResult.imported}, Skipped: {importResult.skipped}</p>
              {importResult.errors?.length > 0 && (
                <ul>
                  {importResult.errors.map((e, i) => (
                    <li key={i} style={{ color: 'red' }}>Row {e.row}: {e.reason}</li>
                  ))}
                </ul>
              )}
            </>
          )}
        </div>
      )}

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Stock</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>₹{p.price}</td>
              <td>{p.stock_quantity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Products;