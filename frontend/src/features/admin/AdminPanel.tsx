import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { SkeletonLoader } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { useLanguage } from '../../context/LanguageContext';
import api from '../../api/client';

interface UserItem {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}

export const AdminPanel: React.FC = () => {
  const { t } = useLanguage();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);
  const [search, setSearch] = useState('');

  const loadUsers = async () => {
    setLoading(true);
    setError(false);
    try {
      // Assuming group 4 implements this endpoint
      const res = await api.get<UserItem[]>('/api/admin/users');
      setUsers(res.data);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const filteredUsers = users.filter(u => 
    u.username.toLowerCase().includes(search.toLowerCase()) || 
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '24px', margin: 0 }}>
          {t('অ্যাডমিন প্যানেল', 'Admin Panel')}
        </h2>
        <input
          type="text"
          placeholder={t('ব্যবহারকারী খুঁজুন...', 'Search users...')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: '8px',
            border: '1px solid #D8D3C5',
            width: '250px'
          }}
        />
      </div>

      <Card style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <SkeletonLoader height="40px" />
            <SkeletonLoader height="40px" />
            <SkeletonLoader height="40px" />
          </div>
        ) : error ? (
          <ErrorState 
            message={t('ব্যবহারকারীদের তালিকা লোড করতে সমস্যা হয়েছে।', 'Failed to load users list.')} 
            onRetry={loadUsers} 
          />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ backgroundColor: '#F9F8F6', borderBottom: '1px solid #D8D3C5' }}>
                  <th style={{ padding: '16px', fontWeight: 600, color: '#5A6E69', fontSize: '14px' }}>ID</th>
                  <th style={{ padding: '16px', fontWeight: 600, color: '#5A6E69', fontSize: '14px' }}>Username</th>
                  <th style={{ padding: '16px', fontWeight: 600, color: '#5A6E69', fontSize: '14px' }}>Email</th>
                  <th style={{ padding: '16px', fontWeight: 600, color: '#5A6E69', fontSize: '14px' }}>Role</th>
                  <th style={{ padding: '16px', fontWeight: 600, color: '#5A6E69', fontSize: '14px' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan={5} style={{ padding: '32px', textAlign: 'center', color: '#5A6E69' }}>
                      {t('কোনো ব্যবহারকারী পাওয়া যায়নি।', 'No users found.')}
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map(u => (
                    <tr key={u.id} style={{ borderBottom: '1px solid #E5E1D5' }}>
                      <td style={{ padding: '16px' }}>{u.id}</td>
                      <td style={{ padding: '16px', fontWeight: 500 }}>{u.username}</td>
                      <td style={{ padding: '16px' }}>{u.email}</td>
                      <td style={{ padding: '16px' }}>
                        <Badge label={u.role === 'admin' ? 'Admin' : 'Farmer'} color={u.role === 'admin' ? 'red' : 'green'} />
                      </td>
                      <td style={{ padding: '16px' }}>
                        <Badge label={u.is_active ? 'Active' : 'Inactive'} color={u.is_active ? 'green' : 'gray'} />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
