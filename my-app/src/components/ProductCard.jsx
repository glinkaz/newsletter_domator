import  { useState } from 'react';
import '../styles/global.css'; 

const ProductCard = ({ product, onDelete, showDeleteButton }) => {
  const [showModal, setShowModal] = useState(false);
  const [editingPrice, setEditingPrice] = useState(false);
  const [price, setPrice] = useState(product.price);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  return (
    <>
      <div
        className="card h-100 shadow-sm position-relative"
        style={{ cursor: 'pointer' }}
        onClick={() => setShowModal(true)}
      >
        {product.ceneo_url && product.ceneo_url.trim() !== '' && (
          <a
            href={product.ceneo_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-warning btn-sm"
            style={{
              position: 'absolute',
              top: '15px',
              right: '15px',
              zIndex: 20,
              fontWeight: 700,
              borderRadius: '16px',
              boxShadow: '0 2px 8px #0002',
              color: '#fff',
              background: '#e34972ff',
              padding: '0.3rem 0.9rem',
              fontSize: '0.95rem',
              opacity: 0.95
            }}
            onClick={e => e.stopPropagation()}
          >
            Porównaj z Ceneo
          </a>
        )}
        <div className="d-flex align-items-center justify-content-center bg-light" style={{ width: '100%', height: '220px', borderRadius: '12px', overflow: 'hidden' }}>
          <img
            src={`http://localhost:5001/product_image/${product.id}`}
            alt={product.name}
            className="card-img-top"
            style={{ maxWidth: '95%', maxHeight: '200px', objectFit: 'contain', display: 'block', margin: '0 auto' }}
          />
        </div>
        <div className="card-body d-flex flex-column" style={{ width: '100%', overflow: 'hidden', paddingBottom: '1.5rem' }}>
          <h3 className="card-title" style={{ fontSize: '1.2rem', fontWeight: 700 }}>{product.name}</h3>
          {showDeleteButton ? (
            <div style={{  alignItems: 'center', gap: '0.5rem', margin: '0.5rem 0' }}>
              {editingPrice ? (
                <>
                  <input
                    type="number"
                    value={price}
                    min="0"
                    step="0.01"
                    onClick={e => e.stopPropagation()}
                    onChange={e => setPrice(e.target.value)}
                    style={{ width: '80px', fontWeight: 700 }}
                  />
                  <button
                    className="btn btn-success btn-sm"
                    disabled={saving}
                    onClick={async e => {
                      e.stopPropagation();
                      setSaving(true);
                      setError(null);
                      try {
                        const res = await fetch(`http://localhost:5001/products/${product.id}/price`, {
                          method: 'PATCH',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ price })
                        });
                        if (!res.ok) throw new Error('Błąd zapisu');
                        setEditingPrice(false);
                      } catch (err) {
                        setError('Błąd zapisu');
                      } finally {
                        setSaving(false);
                      }
                    }}
                  >Zapisz</button>
                  <button
                    className="btn btn-secondary btn-sm"
                    disabled={saving}
                    onClick={e => { e.stopPropagation(); setEditingPrice(false); setPrice(product.price); }}
                  >Anuluj</button>
                </>
              ) : (
                <>
                  <span className="card-text " style={{color: "#c7385e", fontWeight: 900, margin: '10px'}}>{price} zł</span>
                  <button
                    className="btn btn-outline-primary btn-sm"
                    margin = '10px'
                    onClick={e => { e.stopPropagation(); setEditingPrice(true); }}
                  >Edytuj</button>
                </>
              )}
              {error && <span style={{ color: 'red', fontSize: '0.9em' }}>{error}</span>}
            </div>
          ) : (
            <p className="card-text" style={{ margin: '0.5rem 0', color: "#c7385e", fontWeight: 900 }}>{price} zł</p>
          )}
          <p className="card-text" style={{ fontSize: '0.98rem', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {product.description && product.description.length > 80
              ? product.description.slice(0, 80) + '...'
              : product.description}
          </p>
          {showDeleteButton && onDelete && (
            <button
              className="btn btn-danger mt-auto align-self-center"
              onClick={e => { e.stopPropagation(); onDelete(product.id); }}
            >
              Usuń
            </button>
          )}
        </div>
      </div>
      {showModal && (
        <div className="modal fade show" style={{ display: 'block', background: 'rgba(0,0,0,0.7)' }} tabIndex="-1" onClick={() => setShowModal(false)}>
          <div className="modal-dialog modal-lg modal-dialog-centered" onClick={e => e.stopPropagation()}>
            <div className="modal-content p-4 text-center position-relative">
              <img
                src={`http://localhost:5001/product_image/${product.id}`}
                alt={product.name}
                className="img-fluid rounded mb-3"
                style={{ maxHeight: '400px', objectFit: 'contain' }}
              />
              <h2>{product.name}</h2>
              <p className="fs-5 mb-3">{product.description}</p>
              <p className=" fs-4" style={{color: "#c7385e", fontWeight: 900}}>{price} zł</p>
              <button
                type="button"
                className="btn-close position-absolute"
                style={{ top: '1rem', right: '1rem' }}
                aria-label="Close"
                onClick={() => setShowModal(false)}
              ></button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ProductCard;
