
import '../styles/global.css'; 
import ProductCard from "./ProductCard";

const ProductList = ({ products, onDelete, showDeleteButton = false }) => (

  <div className="row">
    {products.map(product => (
      <div className="col-md-4 mb-4" key={product.id}>
        <ProductCard product={product} onDelete={onDelete} showDeleteButton={showDeleteButton} style={{ flex: 1, height: '100%' }} />
      </div>
    ))}
  </div>
);

export default ProductList;
