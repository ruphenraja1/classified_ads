'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function AdPage({ params }) {
  const [ad, setAd] = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState('en');

  useEffect(() => {
    const getParams = async () => {
      const { id } = await params;
      const lang = localStorage.getItem('language') || 'en';
      setLanguage(lang);
      fetch(`http://localhost:8000/api/v1/ads/${id}/`)
        .then(res => res.json())
        .then(data => {
          setAd(data);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    };
    getParams();
  }, [params]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-2xl" style={{ color: 'var(--color-text-muted)' }}>Loading...</div>
    </div>
  );
  
  if (!ad) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="card" style={{ textAlign: 'center' }}>
        <p style={{ fontSize: '1.5rem', color: 'var(--color-text-muted)' }}>
          Ad not found
        </p>
        <Link href="/" className="btn" style={{ marginTop: '1.5rem' }}>
          Go Home
        </Link>
      </div>
    </div>
  );

  const title = ad.title || 'No Title';
  const description = ad.description || 'No Description';
  const location = ad.location || 'No Location';

  return (
    <div className="min-h-screen">
      <header className="header">
        <div className="container">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <Link href="/" style={{ textDecoration: 'none' }}>
              <h2 style={{ margin: 0 }}>Daily Classifieds</h2>
            </Link>
            {/* <h1 style={{ margin: 0 }}>Classified Ad</h1> */}
          </div>
        </div>
      </header>
      
      <main className="section">
        <div className="container">
          <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h1 style={{ 
              marginBottom: '1.5rem',
              color: 'var(--color-dark)',
              fontSize: '2rem',
              lineHeight: 1.3
            }}>
              {title}
            </h1>
            
            <p style={{ 
              fontSize: '1.25rem',
              marginBottom: '2rem',
              color: 'var(--color-text-secondary)',
              lineHeight: 1.8
            }}>
              {description}
            </p>
            
            <div style={{ 
              display: 'grid', 
              gap: '1rem',
              marginBottom: '2rem',
              padding: '1.5rem',
              backgroundColor: 'var(--color-bg-secondary)',
              borderRadius: '12px'
            }}>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'baseline' }}>
                <span style={{ fontWeight: 600, color: 'var(--color-text-muted)' }}>Location:</span>
                <span style={{ fontSize: '1.125rem' }}>{location}, {ad.city}</span>
              </div>
              
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'baseline' }}>
                <span style={{ fontWeight: 600, color: 'var(--color-text-muted)' }}>Posted:</span>
                <span style={{ fontSize: '1.125rem' }}>
                  {new Date(ad.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            
            {ad.images && ad.images.length > 0 && (
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ 
                  marginBottom: '1rem',
                  color: 'var(--color-dark)'
                }}>
                  Images
                </h3>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                  gap: '1rem'
                }}>
                  {ad.images.map((img, i) => (
                    <div 
                      key={i} 
                      style={{ 
                        border: '3px solid var(--color-border)',
                        borderRadius: '12px',
                        overflow: 'hidden'
                      }}
                    >
                      <img 
                        src={`http://localhost:8000${img}`} 
                        alt={`Ad image ${i + 1}`}
                        style={{ width: '100%', height: 'auto', display: 'block' }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div style={{ 
              display: 'flex', 
              gap: '1rem', 
              flexWrap: 'wrap',
              padding: '1.5rem',
              backgroundColor: 'var(--color-bg-secondary)',
              borderRadius: '12px'
            }}>
              <a 
                href={`tel:${ad.phone}`} 
                className="btn"
                style={{ flex: '1', minWidth: '200px', textDecoration: 'none' }}
              >
                📞 Call {ad.phone}
              </a>
              
              {ad.whatsapp && (
                <a 
                  href={`https://wa.me/${ad.whatsapp}`} 
                  className="btn"
                  style={{ 
                    flex: '1', 
                    minWidth: '200px', 
                    textDecoration: 'none',
                    backgroundColor: '#25D366',
                    borderColor: '#128C7E'
                  }}
                >
                  💬 WhatsApp
                </a>
              )}
            </div>
            
            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <Link 
                href={`/category/${ad.category?.toLowerCase()}`}
                className="btn btn-secondary"
                style={{ textDecoration: 'none' }}
              >
                ← Back to {ad.category} Ads
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
