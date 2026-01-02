import  { useState } from 'react';

const NewsletterForm = () => {
  const [email, setEmail] = useState('');

  const handleSubmit = e => {
    e.preventDefault();
    alert(`Subscribed with: ${email}`);
    setEmail('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Subscribe to our newsletter</h2>
      <input
        type="email"
        placeholder="Your email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />
      <button type="submit">Subscribe</button>
    </form>
  );
};

export default NewsletterForm;
