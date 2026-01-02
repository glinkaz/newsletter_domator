import { useEffect, useState } from "react";
import '../App.css';
import '../styles/global.css';
import ProductList from '../components/ProductList';
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
    fetch("http://localhost:5001/products")
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
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          width: '100%',
          background: 'linear-gradient(165deg, #c7385e 0%, #c7385e 60%, #fff 100%)',
          color: '#fff',
          textAlign: 'center',
          padding: '0.3rem 0',
          fontWeight: 700,
          fontSize: '1.15rem',
          letterSpacing: '0.5px',
          boxShadow: '0 2px 8px #0001',
          zIndex: 100,
          margin: 0
        }}
      >
        Jeśli znajdziesz taniej - negocjuj cenę
      </div>
      <div style={{ position: 'relative', minHeight: '100vh', overflow: 'auto' , marginTop: '-1.5rem' }}>
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
            <h2 className="info-modal-title">O nas / Kontakt</h2>
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
      <h1
        style={{
          fontFamily: 'Oswald, Arial Black, Arial, sans-serif',
          color: '#a8002c',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          fontSize: '6rem',
          fontWeight: 700,
          marginTop: '2rem',
          position: 'relative',
          zIndex: 1,
          textShadow: '1px 2px 8px #fff6, 0 2px 0 #fff',
        }}
      >
        Domator
      </h1>
      <nav style={{ marginBottom: "2rem", display: "flex", gap: "1rem", justifyContent: "center", position: 'relative', zIndex: 1 }}>
        {DEPARTMENTS.map((dept) => (
          <button
            key={dept}
            onClick={() => setSelectedDept(dept)}
            style={{
              padding: "0.5rem 1.5rem",
              borderRadius: "20px",
              border: selectedDept === dept ? "2px solid #a8002c" : "1px solid #ccc",
              background: selectedDept === dept ? "#f3e0e4ff" : "#fff",
              color: selectedDept === dept ? "#a8002c" : "#333",
              fontWeight: selectedDept === dept ? "bold" : "normal",
              cursor: "pointer"
            }}
          >
            {dept}
          </button>
        ))}
      </nav>
      <ProductList products={filteredProducts} showDeleteButton={false}/>
  </div>
  </>
  );
};

export default Home;