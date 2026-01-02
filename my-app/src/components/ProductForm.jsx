import  { useState } from 'react';
import '../styles/global.css'; 


const ProductForm = ({ onAdd }) => {
  const [form, setForm] = useState({
    name: '',
    price: '',
    description: '',
    category: '',
    ceneo_url: ''
  });
  const [photoFile, setPhotoFile] = useState(null);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = e => {
    setPhotoFile(e.target.files[0]);
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (!form.name || !form.price) return alert('Name and price are required');
    const formData = new FormData();
    Object.entries(form).forEach(([key, value]) => formData.append(key, value));
    if (photoFile) formData.append('image', photoFile);
    for (let pair of formData.entries()) {
      console.log(pair[0]+ ':', pair[1]);
    }
    onAdd(formData);
  setForm({ name: '', price: '', description: '', category: '', ceneo_url: '' });
    setPhotoFile(null);
    e.target.reset();
  };

  const DEPARTMENTS = ["AGD", "Meble", "Kosmetyki", "Kuchnie", "Drobne"];

  return (
    <form className="admin-form p-4 bg-light rounded shadow-sm" onSubmit={handleSubmit} encType="multipart/form-data">
      <h3 className="mb-4">Dodaj Produkt</h3>
  <input className="form-control mb-3" name="name" placeholder="Name" value={form.name} onChange={handleChange} required />
  <input className="form-control mb-3" name="price" placeholder="Price" value={form.price} onChange={handleChange} required />
  <textarea className="form-control mb-3" name="description" placeholder="Description" value={form.description} onChange={handleChange} />
  <input className="form-control mb-3" name="ceneo_url" placeholder="Ceneo link (opcjonalnie)" value={form.ceneo_url} onChange={handleChange} />
      <select
        className="form-select mb-4"
        name="category"
        value={form.category}
        onChange={handleChange}
        required
      >
        <option value="" disabled>Select Category...</option>
        {DEPARTMENTS.map(dept => (
          <option key={dept} value={dept}>{dept}</option>
        ))}
      </select>
      <input
        className="form-control mb-4"
        type="file"
        name="image"
        accept="image/*"
        onChange={handleFileChange}
      />
      <button type="submit" className="btn btn-primary w-100">Add Product</button>
    </form>
  );
};

export default ProductForm;
