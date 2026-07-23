import { useEffect, useState } from 'react';
import { getProducts, getCustomers, createInvoice } from '../api';

function Billing() {
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [customerId, setCustomerId] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [cart, setCart] = useState([]);
  const [invoiceResult, setInvoiceResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getProducts().then((res) => setProducts(res.data));
    getCustomers().then((res) => setCustomers(res.data));
  }, []);

  const addToCart = () => {
    if (!selectedProduct || quantity <= 0) return;
    const product = products.find((p) => p.id === parseInt(selectedProduct));
    setCart([...cart, { product_id: product.id, name: product.name, price: product.price, quantity: parseInt(quantity) }]);
    setSelectedProduct('');
    setQuantity(1);
  };

  const removeFromCart = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleCreateInvoice = async () => {
    setError(null);
    try {
      const res = await createInvoice({
        customer_id: parseInt(customerId),
        items: cart.map((item) => ({ product_id: item.product_id, quantity: item.quantity })),
      });
      setInvoiceResult(res.data);
      setCart([]);
      setCustomerId('');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  return (
    <div>
      <h2>Create Bill</h2>

      <div>
        <label>Customer: </label>
        <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
          <option value="">Select customer</option>
          {customers.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      <div style={{ marginTop: '10px' }}>
        <label>Product: </label>
        <select value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)}>
          <option value="">Select product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>{p.name} - ₹{p.price}</option>
          ))}
        </select>
        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          style={{ width: '60px', marginLeft: '10px' }}
        />
        <button onClick={addToCart} style={{ marginLeft: '10px' }}>Add to Cart</button>
      </div>

      <h3 style={{ marginTop: '20px' }}>Cart</h3>
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Qty</th>
            <th>Price</th>
            <th>Subtotal</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {cart.map((item, i) => (
            <tr key={i}>
              <td>{item.name}</td>
              <td>{item.quantity}</td>
              <td>₹{item.price}</td>
              <td>₹{item.price * item.quantity}</td>
              <td><button onClick={() => removeFromCart(i)}>Remove</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Total: ₹{total.toFixed(2)}</h3>

      <button onClick={handleCreateInvoice} disabled={!customerId || cart.length === 0}>
        Create Invoice
      </button>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {invoiceResult && (
        <div style={{ marginTop: '20px', border: '1px solid green', padding: '10px' }}>
          <h3>Invoice Created: {invoiceResult.invoice_number}</h3>
          <p>Total: ₹{invoiceResult.total_amount}</p>
          <ul>
            {invoiceResult.items.map((item) => (
              <li key={item.id}>{item.product_name} x {item.quantity} = ₹{item.subtotal}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Billing;