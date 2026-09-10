import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Navigation,
  Phone,
  Clock,
  Search,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  Building2,
  X
} from 'lucide-react';
import { PharmacyItem } from '../types';
import { api } from '../services/api';

interface PharmacyFinderProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PharmacyFinder: React.FC<PharmacyFinderProps> = ({
  isOpen,
  onClose
}) => {
  const [pharmacies, setPharmacies] = useState<PharmacyItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [locPermissionStatus, setLocPermissionStatus] = useState<
    'prompt' | 'granted' | 'denied'
  >('prompt');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && pharmacies.length === 0) {
      // Prompt user or fetch default directory
      fetchPharmacies();
    }
  }, [isOpen]);

  const requestGeolocation = () => {
    if (!navigator.geolocation) {
      setErrorMessage('Geolocation is not supported by your browser.');
      fetchPharmacies(undefined, undefined, searchQuery);
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        setLocPermissionStatus('granted');
        await fetchPharmacies(pos.coords.latitude, pos.coords.longitude);
      },
      (err) => {
        console.warn('Geolocation denied or timed out:', err);
        setLocPermissionStatus('denied');
        setErrorMessage('Location permission was not granted. Showing standard regional pharmacies.');
        fetchPharmacies(undefined, undefined, searchQuery || 'Downtown');
      },
      { timeout: 8000 }
    );
  };

  const fetchPharmacies = async (lat?: number, lon?: number, query?: string) => {
    setLoading(true);
    try {
      const resp = await api.fetchNearbyPharmacies(lat, lon, query);
      setPharmacies(resp.pharmacies);
    } catch (e) {
      console.error('Error loading pharmacies:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPharmacies(undefined, undefined, searchQuery);
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="pharmacy-finder-title"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem'
      }}
    >
      <div
        className="rx-card"
        style={{
          width: '100%',
          maxWidth: '800px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'var(--bg-surface)',
          padding: '1.5rem',
          borderRadius: '20px',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                backgroundColor: 'var(--accent-primary-subtle)',
                color: 'var(--accent-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <MapPin size={20} />
            </div>
            <div>
              <h3 id="pharmacy-finder-title" style={{ fontSize: 'var(--text-lg)', fontWeight: 800 }}>
                Nearby Pharmacies Finder
              </h3>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                Find local pharmacies to fill your prescription and check stock
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'transparent', color: 'var(--text-muted)', padding: '0.4rem' }}
            aria-label="Close Pharmacy Finder"
          >
            <X size={22} />
          </button>
        </div>

        {/* Location Notice & Search Bar */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
            marginBottom: '1rem',
            paddingBottom: '1rem',
            borderBottom: '1px solid var(--border-subtle)'
          }}
        >
          {/* Permission / Geolocation Action */}
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              onClick={requestGeolocation}
              className="btn-primary"
              style={{ padding: '0.55rem 1rem', fontSize: 'var(--text-xs)', borderRadius: '8px' }}
              disabled={loading}
            >
              <Navigation size={15} />
              <span>Use My Current Location</span>
            </button>

            <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', flex: 1, minWidth: '220px' }}>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Or search by City or ZIP Code (e.g. 94102)"
                style={{
                  flex: 1,
                  padding: '0.55rem 0.85rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-strong)',
                  backgroundColor: 'var(--bg-surface-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: 'var(--text-xs)'
                }}
              />
              <button
                type="submit"
                className="btn-secondary"
                style={{ padding: '0.55rem 0.85rem', fontSize: 'var(--text-xs)', borderRadius: '8px' }}
                disabled={loading}
              >
                <Search size={15} />
                <span>Search</span>
              </button>
            </form>
          </div>

          {errorMessage && (
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--accent-warning)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <AlertCircle size={14} />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Explicit Inventory Disclaimer */}
          <div
            style={{
              padding: '0.6rem 0.85rem',
              borderRadius: '8px',
              backgroundColor: 'var(--bg-surface-subtle)',
              border: '1px solid var(--border-subtle)',
              fontSize: 'var(--text-xs)',
              color: 'var(--text-muted)'
            }}
          >
            ℹ️ <strong>Stock Disclaimer:</strong> These are nearby pharmacies where you can check availability. RxDecoder does not track live retail inventory. Please call ahead to confirm medication stock.
          </div>
        </div>

        {/* Pharmacy Listings */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.85rem',
            paddingRight: '0.35rem'
          }}
        >
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              <p>Locating nearby pharmacies...</p>
            </div>
          ) : pharmacies.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              <p>No pharmacies found. Try searching with a different ZIP code or city.</p>
            </div>
          ) : (
            pharmacies.map((pharmacy) => (
              <div
                key={pharmacy.id}
                style={{
                  padding: '1rem',
                  borderRadius: '12px',
                  backgroundColor: 'var(--bg-surface-subtle)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '0.75rem'
                }}
              >
                <div style={{ flex: 1, minWidth: '220px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <Building2 size={16} style={{ color: 'var(--accent-primary)' }} />
                    <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {pharmacy.name}
                    </h4>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        padding: '0.15rem 0.45rem',
                        borderRadius: '4px',
                        backgroundColor: 'var(--accent-primary-subtle)',
                        color: 'var(--accent-primary)'
                      }}
                    >
                      {pharmacy.distance_miles} mi ({pharmacy.distance_km} km)
                    </span>
                  </div>

                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                    📍 {pharmacy.address}
                  </p>

                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                    {pharmacy.phone && (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Phone size={12} /> {pharmacy.phone}
                      </span>
                    )}
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={12} /> {pharmacy.hours_summary}
                    </span>
                  </div>
                </div>

                <a
                  href={pharmacy.google_maps_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary"
                  style={{
                    padding: '0.45rem 0.85rem',
                    fontSize: 'var(--text-xs)',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                >
                  <span>Directions</span>
                  <ExternalLink size={13} />
                </a>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
