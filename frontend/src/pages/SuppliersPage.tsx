import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuthStore } from '../store/authStore';

interface Supplier {
  id: string;
  name: string;
  vat_number?: string;
  country_code: string;
  payment_terms_days: string;
  is_active: boolean;
}

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    vat_number: '',
    country_code: 'GB',
    payment_terms_days: '30'
  });

  // Get token from Zustand store
  const user = useAuthStore((state) => state.user);
  const token = user?.access_token;
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    if (token) {
      loadSuppliers();
    }
  }, [token]);

  const loadSuppliers = async () => {
    if (!token) {
      setError('Not authenticated');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(
        `${apiUrl}/suppliers`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setSuppliers(response.data);
      setError('');
    } catch (err: any) {
      setError('Failed to load suppliers');
      console.error('Error:', err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!token) {
      setError('Not authenticated');
      return;
    }

    try {
      await axios.post(
        `${apiUrl}/suppliers`,
        formData,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setFormData({
        name: '',
        vat_number: '',
        country_code: 'GB',
        payment_terms_days: '30'
      });
      setShowForm(false);
      loadSuppliers();
    } catch (err: any) {
      setError('Failed to add supplier');
      console.error('Error:', err.response?.data || err.message);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Suppliers</h1>
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <button
        onClick={() => setShowForm(!showForm)}
        style={{ marginBottom: '20px', padding: '10px 20px', cursor: 'pointer' }}
      >
        {showForm ? 'Cancel' : 'Add Supplier'}
      </button>

      {showForm && (
        <form onSubmit={handleAddSupplier} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '20px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Name:</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label>VAT Number:</label>
            <input
              type="text"
              value={formData.vat_number}
              onChange={(e) => setFormData({ ...formData, vat_number: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label>Country Code:</label>
            <input
              type="text"
              value={formData.country_code}
              onChange={(e) => setFormData({ ...formData, country_code: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label>Payment Terms (days):</label>
            <input
              type="text"
              value={formData.payment_terms_days}
              onChange={(e) => setFormData({ ...formData, payment_terms_days: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <button type="submit" style={{ padding: '10px 20px', cursor: 'pointer' }}>
            Add Supplier
          </button>
        </form>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #ccc' }}>
              <th style={{ padding: '10px', textAlign: 'left' }}>Name</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>VAT Number</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Country</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Payment Terms</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map((supplier) => (
              <tr key={supplier.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>{supplier.name}</td>
                <td style={{ padding: '10px' }}>{supplier.vat_number || '-'}</td>
                <td style={{ padding: '10px' }}>{supplier.country_code}</td>
                <td style={{ padding: '10px' }}>Net {supplier.payment_terms_days}</td>
                <td style={{ padding: '10px' }}>
                  <span style={{ color: supplier.is_active ? 'green' : 'red' }}>
                    {supplier.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}