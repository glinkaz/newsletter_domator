import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from "../config";
import '../styles/global.css';
import DOMPurify from 'dompurify';

const formatPrice = (priceVal) => {
  if (!priceVal) return null;
  // Check if it's a valid number string
  if (!isNaN(parseFloat(priceVal)) && isFinite(priceVal)) {
    const num = parseFloat(priceVal);
    // If integer, no decimals. If float, 2 decimals.
    const formatted = num % 1 === 0 ? num.toFixed(0) : num.toFixed(2);
    return `${formatted} zł`;
  }
  // Otherwise return text as is
  return priceVal;
};

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
        style={{
          cursor: 'pointer',
          border: (product.visible === false && showDeleteButton) ? '2px solid red' : undefined
        }}
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
        {product.visible === false && showDeleteButton && (
          <span
            className="badge bg-danger"
            style={{
              position: 'absolute',
              top: '55px',
              right: '15px',
              zIndex: 20,
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}
          >
            UKRYTY (Taniej na Ceneo)
          </span>
        )}
        <div className="d-flex align-items-center justify-content-center bg-light" style={{ width: '100%', height: '220px', borderRadius: '12px', overflow: 'hidden' }}>
          {product.content_type && product.content_type.startsWith('video') ? (
            <video
              src={`${API_BASE_URL}/product_image/${product.id}`}
              className="card-img-top"
              style={{ maxWidth: '100%', maxHeight: '200px', objectFit: 'contain', display: 'block', margin: '0 auto' }}
              muted
              loop
              onMouseOver={e => e.target.play()}
              onMouseOut={e => e.target.pause()}
            />
          ) : (
            <img
              src={`${API_BASE_URL}/product_image/${product.id}`}
              alt={product.name}
              className="card-img-top"
              style={{ maxWidth: '95%', maxHeight: '200px', objectFit: 'contain', display: 'block', margin: '0 auto' }}
            />
          )}
        </div>
        <div className="card-body d-flex flex-column" style={{ width: '100%', overflow: 'hidden', paddingBottom: '1.5rem' }}>
          <h3 className="card-title" style={{ fontSize: '1.2rem', fontWeight: 700 }}>{product.name}</h3>

          {showDeleteButton ? (
            <div style={{ alignItems: 'center', gap: '0.5rem', margin: '0.5rem 0' }}>
              {editingPrice ? (
                <>
                  <input
                    type="text"
                    value={price}
                    onClick={e => e.stopPropagation()}
                    onChange={e => setPrice(e.target.value)}
                    style={{ width: '120px', fontWeight: 700 }}
                  />
                  <button
                    className="btn btn-success btn-sm"
                    disabled={saving}
                    onClick={async e => {
                      e.stopPropagation();
                      setSaving(true);
                      setError(null);
                      try {
                        const res = await fetch(`${API_BASE_URL}/products/${product.id}/price`, {
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
                    onClick={e => { e.stopPropagation(); setEditingPrice(false); setPrice(product.price || ''); }}
                  >Anuluj</button>
                </>
              ) : (
                <>
                  {price ? (
                    <span className="card-text " style={{ color: "#c7385e", fontWeight: 900, margin: '10px' }}>
                      {formatPrice(price)}
                    </span>
                  ) : (
                    <span className="text-muted" style={{ margin: '10px', fontStyle: 'italic' }}>Brak ceny</span>
                  )}
                  <button
                    className="btn btn-outline-primary btn-sm"
                    margin='10px'
                    onClick={e => { e.stopPropagation(); setEditingPrice(true); }}
                  >Edytuj</button>
                </>
              )}
              {error && <span style={{ color: 'red', fontSize: '0.9em' }}>{error}</span>}
              {product.ceneo_last_price && (
                <div style={{ fontSize: '0.8rem', color: '#dc3545', marginTop: '4px', width: '100%' }}>
                  Ceneo: {formatPrice(product.ceneo_last_price)}
                </div>
              )}
            </div>
          ) : (
            price ? (
              <p className="card-text" style={{ margin: '0.5rem 0', color: "#c7385e", fontWeight: 900 }}>
                {formatPrice(price)}
              </p>
            ) : null
          )}

          <p className="card-text" style={{ fontSize: '0.98rem', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {(() => {
              if (!product.description) return '';
              const tmp = document.createElement("DIV");
              tmp.innerHTML = product.description;
              const text = tmp.textContent || tmp.innerText || "";
              return text.length > 80 ? text.slice(0, 80) + '...' : text;
            })()}
          </p>

          {showDeleteButton && onDelete && (
            <button
              className="btn btn-danger mt-auto align-self-center"
              onClick={e => { e.stopPropagation(); onDelete(product.id); }}
            >
              Usuń
            </button>
          )}
        </div >
      </div >

      {showModal && (
        <div className="modal fade show" style={{ display: 'block', background: 'rgba(0,0,0,0.7)' }} tabIndex="-1" onClick={() => setShowModal(false)}>
          <div className="modal-dialog modal-lg modal-dialog-centered" onClick={e => e.stopPropagation()}>
            <div className="modal-content p-4 text-center position-relative">
              <button
                type="button"
                className="btn-close position-absolute"
                style={{ top: '1rem', right: '1rem', zIndex: 100 }}
                aria-label="Close"
                onClick={() => setShowModal(false)}
              ></button>

              <ImageGallery product={product} />

              <h2 className="mt-4">{product.name}</h2>
              <div
                className="fs-5 mb-3 text-start"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(product.description) }}
                style={{ wordBreak: 'break-word' }}
              />
              <p className=" fs-4" style={{ color: "#c7385e", fontWeight: 900 }}>
                {formatPrice(product.price)}
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// Internal Component for Gallery / Carousel
const ImageGallery = ({ product }) => {
  const [galleryItems, setGalleryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    fetch(`${API_BASE_URL}/product_images/${product.id}`)
      .then(res => res.json())
      .then(data => {
        // Data is now a list of objects: [{id: 1, content_type: 'image/jpeg'}, ...]
        // Handle backward compatibility for old API return (list of ints)
        if (Array.isArray(data) && typeof data[0] === 'number') {
          setGalleryItems(data.map(id => ({ id, content_type: 'image/jpeg' })));
        } else {
          setGalleryItems(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [product.id]);

  if (loading) return <div className="spinner-border text-primary" role="status"></div>;

  // Fallback if no images found in new table
  if (!galleryItems || galleryItems.length === 0) {
    return (
      <img
        src={`${API_BASE_URL}/product_image/${product.id}`}
        alt={product.name}
        className="img-fluid rounded mb-3"
        style={{ maxHeight: '400px', objectFit: 'contain' }}
      />
    );
  }

  const handlePrev = (e) => {
    e.stopPropagation();
    setCurrentIndex((prev) => (prev === 0 ? galleryItems.length - 1 : prev - 1));
  };

  const handleNext = (e) => {
    e.stopPropagation();
    setCurrentIndex((prev) => (prev === galleryItems.length - 1 ? 0 : prev + 1));
  };

  const currentItem = galleryItems[currentIndex];
  // Safe check if currentItem exists (in case index is out of sync or empty)
  if (!currentItem) return null;

  const isVideo = currentItem.content_type && currentItem.content_type.startsWith('video');

  return (
    <div className="carousel-container position-relative d-inline-block w-100" style={{ maxWidth: '600px', margin: '0 auto' }}>

      {/* Main Slide */}
      <div className="position-relative d-flex justify-content-center align-items-center bg-light rounded mb-3" style={{ minHeight: '300px', maxHeight: '500px' }}>

        {isVideo ? (
          <video
            src={`${API_BASE_URL}/images/${currentItem.id}`}
            controls
            className="img-fluid rounded"
            style={{ maxHeight: '450px', width: '100%', objectFit: 'contain' }}
          />
        ) : (
          <img
            src={`${API_BASE_URL}/images/${currentItem.id}`}
            alt={`Slide ${currentIndex}`}
            className="img-fluid rounded"
            style={{ maxHeight: '450px', width: '100%', objectFit: 'contain' }}
            onClick={() => window.open(`${API_BASE_URL}/images/${currentItem.id}`, '_blank')}
          />
        )}

        {/* Navigation Arrows (only if > 1 item) */}
        {galleryItems.length > 1 && (
          <>
            <button
              className="btn btn-dark position-absolute top-50 start-0 translate-middle-y ms-2"
              style={{ opacity: 0.7, borderRadius: '50%', width: '40px', height: '40px', padding: 0, zIndex: 10 }}
              onClick={handlePrev}
            >
              &#10094;
            </button>
            <button
              className="btn btn-dark position-absolute top-50 end-0 translate-middle-y me-2"
              style={{ opacity: 0.7, borderRadius: '50%', width: '40px', height: '40px', padding: 0, zIndex: 10 }}
              onClick={handleNext}
            >
              &#10095;
            </button>
          </>
        )}
      </div>

      {/* Dots Navigation */}
      {galleryItems.length > 1 && (
        <div className="d-flex justify-content-center gap-2 mb-2">
          {galleryItems.map((item, idx) => (
            <button
              key={idx}
              className={`btn p-0 rounded-circle ${idx === currentIndex ? 'bg-primary' : 'bg-secondary'}`}
              style={{ width: '10px', height: '10px', border: 'none', opacity: idx === currentIndex ? 1 : 0.5, transition: 'all 0.2s' }}
              onClick={(e) => { e.stopPropagation(); setCurrentIndex(idx); }}
              title={item.content_type && item.content_type.startsWith('video') ? "Wideo" : "Zdjęcie"}
            />
          ))}
        </div>
      )}

      <small className="text-muted d-block">{currentIndex + 1} / {galleryItems.length} {isVideo ? '(Wideo)' : ''}</small>
    </div>
  );
};


export default ProductCard;
