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
      <h1>Dashboard</h1>
      <p>Welcome, {user.email}!</p>
      <p>Organization ID: {user.organization_id}</p>
      
      <button 
        onClick={handleLogout}
        style={{ padding: '10px 20px', cursor: 'pointer' }}
      >
        Logout
      </button>
    </div>
  );
}

