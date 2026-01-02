import { useState, useEffect } from "react";
import ProductForm from "../components/ProductForm";
import ProductList from "../components/ProductList";
import LoginForm from "../components/LoginForm";

const Admin = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [products, setProducts] = useState([]);
  useEffect(() => {
    if (loggedIn) {
      fetchProducts();
    }
  }, [loggedIn]);

  const fetchProducts = async () => {
    const res = await fetch("http://localhost:5001/products");
    const data = await res.json();
    setProducts(data);
  };


const handleAdd = async (formData) => {
  try {
    const res = await fetch("http://localhost:5001/products", {
      method: "POST",
      body: formData

    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const product = await res.json();
    setProducts([...products, product]);
  } catch (err) {
    console.error("Error adding product:", err);
  }
};

  const handleDelete = async (id) => {
    await fetch(`http://localhost:5001/products/${id}`, { method: "DELETE" });
    setProducts(products.filter((p) => p.id !== id));
  };

const DEPARTMENTS = [
  "Wszystkie",
  "AGD",
  "Meble Kuchenne",
  "Meble",
  "Kosmetyki",
  "Drobne AGD",
  "Dywany",
  "Tekstylia"
];

  const [selectedDept, setSelectedDept] = useState("Wszystkie");
  const filteredProducts =
    selectedDept === "Wszystkie"
      ? products
      : products.filter((p) => p.category === selectedDept);

    if (!loggedIn) {
    return <LoginForm onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div style={{ justifyContent: "center", width: "100%" }}>
      <h1 style={{fontWeight : 700}}>Panel Admina</h1>
      <ProductForm onAdd={handleAdd} />

      <nav style={{ marginBottom: "2rem", display: "flex", gap: "1rem", justifyContent: "center"}}>
        {DEPARTMENTS.map((dept) => (
          <button
            key={dept}
            onClick={() => setSelectedDept(dept)}
            style={{
              padding: "0.5rem 1.5rem",
              borderRadius: "20px",
              border: selectedDept === dept ? "2px solid #7d5df3" : "1px solid #ccc",
              background: selectedDept === dept ? "#f0f4ff" : "#fff",
              color: selectedDept === dept ? "#7d5df3" : "#333",
              fontWeight: selectedDept === dept ? "bold" : "normal",
              cursor: "pointer"
            }}
          >
            {dept}
          </button>
        ))}
      </nav>
      <ProductList products={filteredProducts} onDelete={handleDelete} showDeleteButton={true}/>
    </div>
  );
};

export default Admin;
