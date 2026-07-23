import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Products from './pages/Products';
import Billing from './pages/Billing';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: '10px', borderBottom: '1px solid #ccc' }}>
        <Link to="/" style={{ marginRight: '15px' }}>Billing</Link>
        <Link to="/products">Products</Link>
      </nav>
      <div style={{ padding: '20px' }}>
        <Routes>
          <Route path="/" element={<Billing />} />
          <Route path="/products" element={<Products />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;