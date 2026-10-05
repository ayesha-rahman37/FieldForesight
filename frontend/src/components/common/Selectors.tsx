import React, { useEffect, useState } from 'react';
import { fetchCrops, fetchRegions } from '../../api/auth';
import { useLanguage } from '../../context/LanguageContext';

interface SelectProps {
  value: string;
  onChange: (val: string) => void;
  options: string[];
  placeholder?: string;
  disabled?: boolean;
}

const BaseSelect: React.FC<SelectProps> = ({ value, onChange, options, placeholder, disabled }) => {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      style={{
        padding: '10px 12px',
        borderRadius: '8px',
        border: '1px solid #D8D3C5',
        backgroundColor: '#FFFFFF',
        fontSize: '15px',
        outline: 'none',
        minWidth: '180px',
        fontFamily: 'inherit',
        color: '#004741',
      }}
    >
      <option value="" disabled>{placeholder}</option>
      {options.map((opt) => (
        <option key={opt} value={opt}>{opt}</option>
      ))}
    </select>
  );
};

export const CropSelector: React.FC<{ value: string; onChange: (val: string) => void }> = ({ value, onChange }) => {
  const { t } = useLanguage();
  const [crops, setCrops] = useState<string[]>([]);

  useEffect(() => {
    fetchCrops().then(setCrops).catch(console.error);
  }, []);

  return <BaseSelect value={value} onChange={onChange} options={crops} placeholder={t('ফসল নির্বাচন করুন', 'Select Crop')} />;
};

export const RegionSelector: React.FC<{ value: string; onChange: (val: string) => void }> = ({ value, onChange }) => {
  const { t } = useLanguage();
  const [regions, setRegions] = useState<string[]>([]);

  useEffect(() => {
    fetchRegions().then(setRegions).catch(console.error);
  }, []);

  return <BaseSelect value={value} onChange={onChange} options={regions} placeholder={t('অঞ্চল নির্বাচন করুন', 'Select Region')} />;
};

export const VarietySelector: React.FC<{ value: string; onChange: (val: string) => void }> = ({ value, onChange }) => {
  const { t } = useLanguage();
  const varieties = [
    t('স্থানীয় জাত', 'Local Variety'),
    t('উচ্চ ফলনশীল জাত (HYV)', 'High Yielding Variety (HYV)')
  ];
  return <BaseSelect value={value} onChange={onChange} options={varieties} placeholder={t('জাত নির্বাচন করুন', 'Select Variety')} />;
};
