import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    return <p>Loading...</p>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h1>Dashboard</h1>
          <p>Welcome, {user.email}!</p>
        </div>
        <button 
          onClick={handleLogout}
          style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Logout
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div 
          onClick={() => navigate('/suppliers')}
          style={{
            padding: '20px',
            border: '1px solid #ccc',
            borderRadius: '8px',
            cursor: 'pointer',
            backgroundColor: '#f5f5f5',
            transition: 'all 0.3s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e0e0e0'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
        >
          <h2>Suppliers</h2>
          <p>Manage your suppliers and vendor information</p>
        </div>

        <div 
          onClick={() => navigate('/invoices')}
          style={{
            padding: '20px',
            border: '1px solid #ccc',
            borderRadius: '8px',
            cursor: 'pointer',
            backgroundColor: '#f5f5f5',
            transition: 'all 0.3s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e0e0e0'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
        >
          <h2>Invoices</h2>
          <p>View and manage invoices with three-way matching</p>
        </div>
      </div>
    </div>
  );
}