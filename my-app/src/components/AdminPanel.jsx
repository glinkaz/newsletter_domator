import { useState } from 'react';
import ProductForm from './ProductForm';

const AdminPanel = () => {
  const [products, setProducts] = useState([products]);

  const handleAddProduct = product => {
    setProducts(prev => [...prev, product]);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: 'auto' }}>
      <h1>🛠️ Admin Panel</h1>
      <ProductForm onAdd={handleAddProduct} />
    </div>
  );
};

export default AdminPanel;
