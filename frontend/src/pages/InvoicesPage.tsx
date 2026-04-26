import { useState, useEffect } from 'react';
import axios from 'axios';

interface Invoice {
  id: string;
  invoice_number: string;
  gross_amount: number;
  vat_amount: number;
  total_amount: number;
  status: string;
  po_matched: boolean;
  gr_matched: boolean;
  created_at: string;
}

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const token = localStorage.getItem('access_token');
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    loadInvoices();
  }, [statusFilter]);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const url = statusFilter 
        ? `${apiUrl}/invoices?status=${statusFilter}`
        : `${apiUrl}/invoices`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInvoices(response.data);
      setError('');
    } catch (err: any) {
      setError('Failed to load invoices');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'matched':
        return '#4caf50';
      case 'exception':
        return '#ff9800';
      case 'approved':
        return '#2196f3';
      case 'paid':
        return '#4caf50';
      default:
        return '#666';
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Invoices</h1>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={{ marginBottom: '20px' }}>
        <label>Filter by Status:</label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ marginLeft: '10px', padding: '8px' }}
        >
          <option value="">All</option>
          <option value="draft">Draft</option>
          <option value="submitted">Submitted</option>
          <option value="matched">Matched</option>
          <option value="exception">Exception</option>
          <option value="approved">Approved</option>
          <option value="paid">Paid</option>
        </select>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #ccc' }}>
              <th style={{ padding: '10px', textAlign: 'left' }}>Invoice #</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Gross Amount</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>VAT</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Total</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>PO Match</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>GR Match</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice) => (
              <tr key={invoice.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>{invoice.invoice_number}</td>
                <td style={{ padding: '10px' }}>£{invoice.gross_amount.toFixed(2)}</td>
                <td style={{ padding: '10px' }}>£{invoice.vat_amount.toFixed(2)}</td>
                <td style={{ padding: '10px' }}>£{invoice.total_amount.toFixed(2)}</td>
                <td style={{ padding: '10px' }}>
                  <span style={{ color: invoice.po_matched ? 'green' : 'red' }}>
                    {invoice.po_matched ? '✓' : '✗'}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>
                  <span style={{ color: invoice.gr_matched ? 'green' : 'red' }}>
                    {invoice.gr_matched ? '✓' : '✗'}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>
                  <span style={{ color: getStatusColor(invoice.status), fontWeight: 'bold' }}>
                    {invoice.status}
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