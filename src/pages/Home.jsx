import React, { useState, useEffect } from "react";
import '../App.css';
import '../styles/global.css';
import ProductList from '../components/ProductList';
import { API_BASE_URL } from "../config";
if (typeof document !== 'undefined' && !document.getElementById('oswald-font')) {
  const fontLink = document.createElement('link');
  fontLink.href = 'https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap';
  fontLink.rel = 'stylesheet';
  fontLink.id = 'oswald-font';
  document.head.appendChild(fontLink);
}


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

const Home = () => {
  const [products, setProducts] = useState([]);
  const [selectedDept, setSelectedDept] = useState("Wszystkie");
  const [showInfo, setShowInfo] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/products`)
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched products:", data);
        setProducts(data);
      })
      .catch((err) => console.error("Error fetching products:", err));
  }, []);

  const filteredProducts =
    selectedDept ===
      "Wszystkie"
      ? products
      :
      products.filter((p) => p.category === selectedDept);

  return (
    <>
      <div
        className="top-info-bar"
      >
        Jeśli znajdziesz taniej - negocjuj cenę
      </div>
      <div className="main-content" >
        <button
          className="info-btn"
          onClick={() => setShowInfo(true)}

        >
          Kontakt
        </button>

        {showInfo && (
          <div className="info-modal-overlay" onClick={() => setShowInfo(false)}>
            <div className="info-modal" onClick={e => e.stopPropagation()}>
              <button
                className="info-modal-close"
                onClick={() => setShowInfo(false)}
                aria-label="Zamknij"
              >
                ×
              </button>
              <h2 className="info-modal-title">Kontakt</h2>
              <p className="info-modal-content">
                <br />

                <b>E-mail:</b><br />
                Meble: <a href="mailto:domatorsklep.net@gmail.com">domatorsklep.net@gmail.com</a><br />
                AGD/RTV Myszyniec: <a href="mailto:domatormyszy@wp.pl">domatormyszy@wp.pl</a><br />
                Drogeria Myszyniec: <a href="mailto:domator.kosm@wp.pl">domator.kosm@wp.pl</a><br />
                Drogeria Łyse: <a href="mailto:domator.lyse@o2.pl">domator.lyse@o2.pl</a><br />
                AGD/RTV Łyse: <a href="mailto:domatorlyse@gmail.com">domatorlyse@gmail.com</a><br />
                <br />
                <b>Tel: <a href="tel:+48 531 021 973">+48 531 021 973</a></b><br />
                <br />
                <b>Adres:</b><br />
                ul. Poległych 28, 07-430 Myszyniec<br />
                ul. Poległych 3, 07-430 Myszyniec<br />
                ul. Kościelna 2, 07-437 Łyse<br />
              </p>
              <p className="info-modal-footer">
                &copy; {new Date().getFullYear()} Domator. Wszelkie prawa zastrzeżone.
              </p>
            </div>
          </div>
        )}

        <div className="yellow-bg-left" />
        <div className="yellow-bg-right" />
        <div className="yellow-bg-bottom" />
        <h1 className="main-title">
          Domator
        </h1>
        <nav className="category-nav">
          {DEPARTMENTS.map((dept) => (
            <button
              key={dept}
              onClick={() => setSelectedDept(dept)}
              className={`category-btn ${selectedDept === dept ? 'active' : 'inactive'}`}
            >
              {dept}
            </button>
          ))}
        </nav>
        <ProductList products={filteredProducts} showDeleteButton={false} />
      </div >
    </>
  );
};

export default Home;