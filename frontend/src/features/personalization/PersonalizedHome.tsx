import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Loader } from '../../components/common/Loader';
import { ErrorState } from '../../components/common/ErrorState';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { getUserPreference, saveUserPreference } from '../../api/personalization';
import { fetchCrops, fetchRegions } from '../../api/auth';
import type { UserPreference } from './types';

interface PersonalizedHomeProps {
  onSelectionChange: (crop: string, region: string) => void;
  currentCrop: string;
  currentRegion: string;
}

export const PersonalizedHome: React.FC<PersonalizedHomeProps> = ({
  onSelectionChange,
  currentCrop,
  currentRegion,
}) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [pref, setPref] = useState<UserPreference | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const [cropList, setCropList] = useState<string[]>([]);
  const [regionList, setRegionList] = useState<string[]>([]);

  const loadData = async () => {
    setLoading(true);
    setError(false);
    try {
      const [crops, regions] = await Promise.all([fetchCrops(), fetchRegions()]);
      setCropList(crops);
      setRegionList(regions);

      if (user) {
        const p = await getUserPreference(user.id);
        setPref(p);
        if (p.last_crop && p.last_region) {
          onSelectionChange(p.last_crop, p.last_region);
        }
      }
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user?.id]);

  const handleCropChange = async (newCrop: string) => {
    onSelectionChange(newCrop, currentRegion);
    if (user && currentRegion) {
      await saveUserPreference({ user_id: user.id, crop: newCrop, region: currentRegion });
      setPref((prev) => ({ ...prev, user_id: user.id, last_crop: newCrop, last_region: currentRegion }));
    }
  };

  const handleRegionChange = async (newRegion: string) => {
    onSelectionChange(currentCrop, newRegion);
    if (user && currentCrop) {
      await saveUserPreference({ user_id: user.id, crop: currentCrop, region: newRegion });
      setPref((prev) => ({ ...prev, user_id: user.id, last_crop: currentCrop, last_region: newRegion }));
    }
  };

  if (loading) {
    return <Loader message={t('ব্যক্তিগত পছন্দসমূহ লোড করা হচ্ছে...', 'Loading personal preferences...')} />;
  }

  if (error) {
    return <ErrorState message={t('তথ্য লোড করতে সমস্যা হয়েছে', 'Failed to load preferences')} onRetry={loadData} />;
  }

  const username = user?.username || t('কৃষক ভাই', 'Farmer');
  const hasLastSelection = pref?.last_crop && pref?.last_region;

  return (
    <Card>
      <div style={{ marginBottom: '20px' }}>
        <h1>{t(`স্বাগতম, ${username}`, `Welcome, ${username}`)}</h1>
        <p style={{ color: '#5A6E69', marginTop: '4px' }}>
          {t(
            'আপনার খামারের ফসল এবং অঞ্চলের সঠিক পূর্বাভাস দেখার জন্য পছন্দ নির্বাচন করুন।',
            'Select crop and region to view accurate yield predictions for your farm.'
          )}
        </p>
      </div>

      {hasLastSelection ? (
        <div
          onClick={() => {
            if (pref.last_crop && pref.last_region) {
              onSelectionChange(pref.last_crop, pref.last_region);
            }
          }}
          className="interactive-card"
          style={{
            padding: '16px',
            backgroundColor: '#E8F4F1',
            borderRadius: '12px',
            border: '1px solid #4A8B7C',
            marginBottom: '20px',
            cursor: 'pointer',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <span className="caption" style={{ color: '#004741', fontWeight: 600 }}>
              {t('দ্রুত পুনঃসূচনা', 'Quick Resume')}
            </span>
            <p style={{ fontSize: '16px', fontWeight: 600, color: '#004741', marginTop: '2px' }}>
              {t(`আপনার শেষ নির্বাচন: ${pref.last_crop}, ${pref.last_region}`, `Your last selection: ${pref.last_crop}, ${pref.last_region}`)}
            </p>
          </div>
          <span style={{ fontSize: '14px', fontWeight: 600, color: '#004741' }}>
            {t('সক্রিয় করুন →', 'Activate →')}
          </span>
        </div>
      ) : (
        /* Outlined, lighter instructional banner */
        <div
          style={{
            padding: '14px 18px',
            backgroundColor: 'transparent',
            borderRadius: '12px',
            border: '1.5px dashed #D8D3C5',
            marginBottom: '20px',
            textAlign: 'center',
          }}
        >
          <p style={{ fontWeight: 500, color: '#5A6E69', fontSize: '14px' }}>
            {t('শুরু করতে নিচে ফসল ও অঞ্চল নির্বাচন করুন', 'Select a crop and region below to get started')}
          </p>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        <div>
          <label style={{ display: 'block', fontWeight: 600, color: '#004741', marginBottom: '8px', fontSize: '14px' }}>
            {t('ফসল', 'Crop')}
          </label>
          <select
            value={currentCrop}
            onChange={(e) => handleCropChange(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #D8D3C5',
              backgroundColor: '#FFFFFF',
              fontSize: '15px',
              color: '#004741',
              fontWeight: 500,
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="">{t('-- ফসল বেছে নিন --', '-- Select Crop --')}</option>
            {cropList.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontWeight: 600, color: '#004741', marginBottom: '8px', fontSize: '14px' }}>
            {t('অঞ্চল', 'Region')}
          </label>
          <select
            value={currentRegion}
            onChange={(e) => handleRegionChange(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #D8D3C5',
              backgroundColor: '#FFFFFF',
              fontSize: '15px',
              color: '#004741',
              fontWeight: 500,
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="">{t('-- অঞ্চল বেছে নিন --', '-- Select Region --')}</option>
            {regionList.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
      </div>
    </Card>
  );
};
