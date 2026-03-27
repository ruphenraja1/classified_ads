'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function PostPage() {
  const [cities, setCities] = useState([]);
  const [citiesAllLangs, setCitiesAllLangs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [imageUploadEnabled, setImageUploadEnabled] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [otpValue, setOtpValue] = useState('');
  const [images, setImages] = useState([]);
   const [errors, setErrors] = useState({});
   const [language, setLanguage] = useState('en');
   const [labels, setLabels] = useState({});
   const [userMessages, setUserMessages] = useState({});
   const [devMode, setDevMode] = useState(false);
   const [citySearchInput, setCitySearchInput] = useState('');
   const [showCityDropdown, setShowCityDropdown] = useState(false);
  const [form, setForm] = useState({
    title: '',
    description: '',
    // price: '',
    location: '',
    city: '',
    category: '',
    phone: '',
    whatsapp: '',
  });

  // Do not auto-select a city by default. User must choose explicitly.

  // Sync language when returning from another page (back button)
  useEffect(() => {
    const syncLanguageFromStorage = () => {
      try {
        const savedLang = localStorage.getItem('language') || 'en';
        console.log('Post page syncing language:', savedLang);
        setLanguage(savedLang);
      } catch (e) {
        console.error('Error syncing from localStorage:', e);
      }
    };

    // Sync immediately
    syncLanguageFromStorage();

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        console.log('Post page became visible, syncing');
        syncLanguageFromStorage();
      }
    };

    const handlePageShow = (event) => {
      console.log('Post page show event fired, persisted:', event.persisted);
      syncLanguageFromStorage();
    };

    const handleStorageChange = (e) => {
      if (e.key === 'language' || e.key === null) {
        console.log('Post storage changed, syncing');
        syncLanguageFromStorage();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('pageshow', handlePageShow);
    window.addEventListener('storage', handleStorageChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('pageshow', handlePageShow);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  useEffect(() => {
    const lang = localStorage.getItem('language') || 'en';
    setLanguage(lang);

    // Fetch labels from LOV with language
    fetch(`http://localhost:8000/api/v1/lov/?type=UI_LABEL&language=${lang}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        const items = data.results || data || [];
        const labelMap = {};
        items.forEach(item => {
          labelMap[item.lic] = item.display_name;
        });
        setLabels(labelMap);
      })
      .catch(err => console.error('Error fetching labels:', err));

    // Fetch user messages from LOV with language
    fetch(`http://localhost:8000/api/v1/lov/?type=USER_MSG_1&language=${lang}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        const items = data.results || data || [];
        const messageMap = {};
        items.forEach(item => {
          messageMap[item.lic] = item.description;
        });
        setUserMessages(messageMap);
      })
      .catch(err => console.error('Error fetching user messages:', err));

    // Fetch cities in both languages for cross-language search
    Promise.all([
      fetch(`http://localhost:8000/api/v1/lov/?type=CITY&language=en`),
      fetch(`http://localhost:8000/api/v1/lov/?type=CITY&language=ta`)
    ])
      .then(([resEn, resTa]) => {
        return Promise.all([resEn.json(), resTa.json()]);
      })
      .then(([dataEn, dataTa]) => {
        let itemsEn = Array.isArray(dataEn.results) ? dataEn.results : (Array.isArray(dataEn) ? dataEn : []);
        let itemsTa = Array.isArray(dataTa.results) ? dataTa.results : (Array.isArray(dataTa) ? dataTa : []);
        
        // Create a map: lic -> { en: name, ta: name }
        const cityMap = {};
        itemsEn.forEach(item => {
          if (!cityMap[item.lic]) cityMap[item.lic] = {};
          cityMap[item.lic].en = item.display_name;
          cityMap[item.lic].order = item.order || 0;
        });
        itemsTa.forEach(item => {
          if (!cityMap[item.lic]) cityMap[item.lic] = {};
          cityMap[item.lic].ta = item.display_name;
        });
        
        // Store all cities for search
        const allCities = Object.entries(cityMap).map(([lic, names]) => ({
          id: lic,
          en: names.en || '',
          ta: names.ta || '',
          order: names.order || 0
        }));
        setCitiesAllLangs(allCities);
        
        // Create sorted list for selected language
        const sortedByOrder = allCities.sort((a, b) => {
          if (a.order !== b.order) return a.order - b.order;
          return (a[lang] || '').localeCompare(b[lang] || '');
        });
        setCities(sortedByOrder.map(item => ({ id: item.id, name: item[lang] || '' })));
      })
      .catch(err => console.error('Error fetching cities:', err));

    // Fetch categories from LOV with language
    fetch(`http://localhost:8000/api/v1/lov/?type=CATEGORY&language=${lang}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        const items = data.results || data || [];
        setCategories(items.map(item => ({ value: item.lic, name: item.display_name })));
      })
      .catch(err => console.error('Error fetching categories:', err));

    // Check if image upload is enabled
    fetch('http://localhost:8000/api/v1/lov/?type=UI_CONTROL&lic=ENABLE_IMAGE_UPLOAD')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        const items = data.results || data || [];
        if (items.length > 0 && items[0].display_name === 'Enable Image Upload') {
          setImageUploadEnabled(true);
        }
      })
      .catch(err => console.error('Error checking image upload:', err));

    // Check if dev mode for post ad without OTP
    fetch('http://localhost:8000/api/v1/lov/?type=ENABLE_POST_AD_DEV&lic=Y')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        const items = data.results || data || [];
        if (items.length > 0 && items[0].display_name === 'Y') {
          setDevMode(true);
        }
      })
      .catch(err => console.error('Error checking dev mode:', err));
  }, [language]);



  const sendOtp = async () => {
    if (!form.phone || !form.phone.match(/^\+91\d{10}$/)) {
      setErrors({ phone: 'Phone number must be in format +91XXXXXXXXXX.' });
      return;
    }
    setErrors({});
    const res = await fetch('http://localhost:8000/api/v1/send-otp/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: form.phone }),
    });
    if (res.ok) {
      const data = await res.json();
      setOtpSent(true);
      alert('OTP sent!');
    } else {
      const text = await res.text();
      try {
        const err = JSON.parse(text);
        setErrors(err);
      } catch {
        setErrors({ error: `Server error: ${res.status}` });
      }
    }
  };

  const verifyOtp = async () => {
    if (!otpValue) {
      setErrors({ otp: 'Please enter OTP' });
      return;
    }
    const res = await fetch('http://localhost:8000/api/v1/verify-otp/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: form.phone, otp: otpValue }),
    });
    const text = await res.text();
    try {
      const data = JSON.parse(text);
      if (data.valid) {
        setOtpVerified(true);
        alert('OTP verified!');
        setErrors({});
      } else {
        setErrors({ otp: 'Invalid OTP' });
      }
    } catch {
      setErrors({ otp: 'Server error, please try again' });
    }
  };

  const hasExcessiveRepetition = (text, limit = 0.5) => {
    const t = text.replace(/\s/g, "");
    if (!t) return true;
    const freq = {};
    for (const c of t) freq[c] = (freq[c] || 0) + 1;
    return Math.max(...Object.values(freq)) / t.length > limit;
  };

  const hasLowDiversity = (text, minRatio = 0.1) => {
    const t = text.replace(/\s/g, "");
    if (!t) return true;
    return new Set(t).size / t.length < minRatio;
  };

  const hasLowVowelRatio = (text, minRatio = 0.15) => {
    const letters = text.replace(/[^a-zA-Z]/g, "");
    if (!letters) return true;
    const vowels = (letters.match(/[aeiou]/gi) || []).length;
    return vowels / letters.length < minRatio;
  };

  const hasTooManySpecialChars = (text) => {
    const special = text.replace(/[a-zA-Z0-9\s]/g, "").length;
    return special / text.length > 0.3;
  };

  const containsWords = (text) => {
    return /\b[a-zA-Z]{2,}\b/.test(text);
  };

  const looksLikeGibberish = (text) => {
    return /^[^a-zA-Z]*$/.test(text) || /(.)\1{5,}/.test(text) || /(.)\1{3,}.*\1{3,}/.test(text);
  };

  const validateTextFrontend = (text) => {
    // Skip validation for non-ASCII text (e.g., Tamil)
    if (/[^\x00-\x7F]/.test(text)) return null;

    if (!text || text.trim().length < 5)
      return "Text is too short or empty.";
    if (hasExcessiveRepetition(text) || hasLowDiversity(text) || hasLowVowelRatio(text) || hasTooManySpecialChars(text) || !containsWords(text) || looksLikeGibberish(text))
      return "Invalid content detected. Please provide meaningful and appropriate text.";
    return null; // valid
  };

  // Filter cities based on search input (search in both EN and TA, display in selected language)
  const filteredCities = citiesAllLangs.filter(city => {
    const searchLower = citySearchInput.toLowerCase();
    // Search in English name, Tamil name, or LIC (for cross-language support)
    const matchesEn = (city.en || '').toLowerCase().includes(searchLower);
    const matchesTa = (city.ta || '').toLowerCase().includes(searchLower);
    const matchesLic = city.id.toLowerCase().includes(searchLower);
    return matchesEn || matchesTa || matchesLic;
  }).map(city => ({
    id: city.id,
    // Display in selected language, fallback to other language if not available
    name: city[language] || city[language === 'en' ? 'ta' : 'en'] || '',
    key: city.id
  }));

  const handleCitySelectFromDropdown = (cityId, cityName) => {
    setForm({...form, city: cityId});
    setCitySearchInput(cityName);
    setShowCityDropdown(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!devMode && !otpVerified) {
      alert('Please verify OTP first');
      return;
    }
    // Validate required fields
    const requiredFields = ['title', 'description', 'location', 'city', 'category', 'phone'];
    const newErrors = {};
    requiredFields.forEach(field => {
      if (!form[field] || form[field].trim() === '') {
        newErrors[field] = `${field.charAt(0).toUpperCase() + field.slice(1)} is required.`;
      }
    });

    // Validate city is properly selected
    if (!form.city) {
      newErrors.city = 'Please select a city from the dropdown.';
    }

    // Frontend text validation
    const titleError = validateTextFrontend(form.title);
    if (titleError) {
      newErrors.title = titleError;
    }
    const descError = validateTextFrontend(form.description);
    if (descError) {
      newErrors.description = descError;
    }
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    const data = new FormData();
    data.append('title', form.title);
    data.append('description', form.description);
    data.append('location', form.location);
    // data.append('price', form.price || '');
    data.append('city', form.city);
    data.append('category', form.category);
    data.append('phone', form.phone);
    data.append('whatsapp', form.whatsapp || '');
    images.forEach(img => data.append('images', img));
    const res = await fetch('http://localhost:8000/api/v1/ads/', {
      method: 'POST',
      body: data,
    });
    const text = await res.text();
    try {
      const responseData = JSON.parse(text);
      if (res.ok) {
        alert(responseData.message || 'Ad posted!');
        // Reset form and errors
        setForm({
          title: '', description: '', location: '', city: '', category: '',
          phone: '', whatsapp: ''
        });
        setCitySearchInput('');
        setImages([]);
        setOtpSent(false);
        setOtpVerified(false);
        setErrors({});
      } else {
        setErrors(responseData);
      }
    } catch {
      setErrors({ error: 'Server error, please try again' });
    }
  };

  return (
    <div className="min-h-screen">
      <header className="header">
        <div className="container">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <Link href="/" style={{ textDecoration: 'none' }}>
              <h2 style={{ margin: 0 }}>Daily Classifieds</h2>
            </Link>
            <h1 style={{ margin: 0 }}>Post a Classified Ad</h1>
          </div>
        </div>
      </header>
      
      <main className="section">
        <div className="container">
          <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
            {Object.keys(errors).length > 0 && (
              <div className="card" style={{ 
                backgroundColor: '#FEE2E2', 
                borderColor: '#EF4444',
                marginBottom: '2rem',
                padding: '1.5rem'
              }}>
                {Object.entries(errors).map(([key, value]) => (
                  <p key={key} style={{ 
                    color: '#DC2626', 
                    margin: '0.5rem 0',
                    fontWeight: 600
                  }}>
                    {key}: {value}
                  </p>
                ))}
              </div>
            )}
            
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '1.125rem', 
                  fontWeight: 600, 
                  marginBottom: '0.75rem',
                  color: 'var(--color-text-primary)'
                }}>
                  {labels.TITLE_LABEL || 'Title'}
                </label>
                <input 
                  type="text" 
                  value={form.title} 
                  onChange={e => setForm({...form, title: e.target.value})} 
                  className="input" 
                  required 
                  maxLength={30} 
                />
              </div>
              
              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '1.125rem', 
                  fontWeight: 600, 
                  marginBottom: '0.75rem',
                  color: 'var(--color-text-primary)'
                }}>
                  {labels.DESC_LABEL || 'Description'}
                </label>
                <textarea 
                  value={form.description} 
                  onChange={e => setForm({...form, description: e.target.value})} 
                  className="input" 
                  style={{ minHeight: '150px', resize: 'vertical' }}
                  required 
                />
              </div>
              

              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '1.125rem', 
                  fontWeight: 600, 
                  marginBottom: '0.75rem',
                  color: 'var(--color-text-primary)'
                }}>
                  {labels.CITY_LABEL || 'City'}
                </label>
                <div className="relative">
                  <input 
                    type="text" 
                    value={citySearchInput}
                    onChange={e => {
                      setCitySearchInput(e.target.value);
                      setShowCityDropdown(true);
                    }}
                    onFocus={() => { setShowCityDropdown(true); setCitySearchInput(''); }}
                    onBlur={() => setTimeout(() => setShowCityDropdown(false), 200)}
                    placeholder="Search City..."
                    className="input" 
                    required={!form.city}
                    autoComplete="off"
                  />
                  {showCityDropdown && (
                    <ul className="select-dropdown" style={{ 
                      position: 'absolute', 
                      top: '100%', 
                      left: 0, 
                      right: 0, 
                      zIndex: 10, 
                      marginTop: '0.5rem' 
                    }}>
                      {filteredCities.length > 0 ? (
                        filteredCities.map(c => (
                          <li key={c.id} onClick={() => handleCitySelectFromDropdown(c.id, c.name)}>
                            {c.name}
                          </li>
                        ))
                      ) : (
                        <li style={{ color: 'var(--color-text-muted)' }}>No cities found</li>
                      )}
                    </ul>
                  )}
                </div>
                
                <p style={{ 
                  fontSize: '0.9rem', 
                  color: 'var(--color-text-muted)',
                  marginTop: '0.5rem',
                  fontStyle: 'italic',
                  lineHeight: 1.4
                }}>
                  💡 {userMessages.WHEN_NO_CITY || 'If your city is not in the list, please select the nearest district name from the dropdown above, and mention your exact city/village name in the Location/Address field below.'}
                </p>
              </div>
                            <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '1.125rem', 
                  fontWeight: 600, 
                  marginBottom: '0.75rem',
                  color: 'var(--color-text-primary)'
                }}>
                  {labels.LOCATION_LABEL || 'Location'}
                </label>
                <input 
                  type="text" 
                  value={form.location} 
                  onChange={e => setForm({...form, location: e.target.value})} 
                  className="input" 
                  required 
                  maxLength={170} 
                />
              </div>
              
              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '1.125rem', 
                  fontWeight: 600, 
                  marginBottom: '0.75rem',
                  color: 'var(--color-text-primary)'
                }}>
                  {labels.CATEGORY_LABEL || 'Category'}
                </label>
                <select 
                  value={form.category} 
                  onChange={e => setForm({...form, category: e.target.value})} 
                  className="input" 
                  style={{ cursor: 'pointer' }}
                  required
                >
                  <option value="">Select category</option>
                  {categories.map(c => <option key={c.value} value={c.value}>{c.name}</option>)}
                </select>
              </div>
              
              {!devMode && (
                <div>
                  <label style={{ 
                    display: 'block', 
                    fontSize: '1.125rem', 
                    fontWeight: 600, 
                    marginBottom: '0.75rem',
                    color: 'var(--color-text-primary)'
                  }}>
                    {labels.PHONE_LABEL || 'Phone'}
                  </label>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <input 
                      type="tel" 
                      value={form.phone} 
                      onChange={e => setForm({...form, phone: e.target.value})} 
                      className="input" 
                      style={{ flex: '1', minWidth: '200px' }}
                      required 
                    />
                    <button 
                      type="button" 
                      onClick={sendOtp} 
                      className="btn"
                      style={{ whiteSpace: 'nowrap' }}
                    >
                      {labels.SEND_OTP || 'Send OTP'}
                    </button>
                  </div>
                </div>
              )}
              
              {!devMode && otpSent && (
                <div>
                  <label style={{ 
                    display: 'block', 
                    fontSize: '1.125rem', 
                    fontWeight: 600, 
                    marginBottom: '0.75rem',
                    color: 'var(--color-text-primary)'
                  }}>
                    {labels.VERIFY_OTP_LABEL || 'OTP'}
                  </label>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <input 
                      type="text" 
                      value={otpValue} 
                      onChange={e => setOtpValue(e.target.value)} 
                      className="input" 
                      style={{ flex: '0 0 150px' }}
                    />
                    <button 
                      type="button" 
                      onClick={verifyOtp} 
                      className="btn"
                      style={{ whiteSpace: 'nowrap' }}
                    >
                      {labels.VERIFY_OTP || 'Verify OTP'}
                    </button>
                  </div>
                </div>
              )}
              
              {devMode && (
                <div>
                  <label style={{ 
                    display: 'block', 
                    fontSize: '1.125rem', 
                    fontWeight: 600, 
                    marginBottom: '0.75rem',
                    color: 'var(--color-text-primary)'
                  }}>
                    {labels.PHONE_LABEL || 'Phone'}
                  </label>
                  <input 
                    type="tel" 
                    value={form.phone} 
                    onChange={e => setForm({...form, phone: e.target.value})} 
                    className="input" 
                    style={{ maxWidth: '300px' }}
                    required 
                  />
                </div>
              )}
              
              {imageUploadEnabled && (
                <div>
                  <label style={{ 
                    display: 'block', 
                    fontSize: '1.125rem', 
                    fontWeight: 600, 
                    marginBottom: '0.75rem',
                    color: 'var(--color-text-primary)'
                  }}>
                    {labels.IMAGES_LABEL || 'Images (up to 5)'}
                  </label>
                  <input 
                    type="file" 
                    multiple 
                    accept="image/*" 
                    onChange={e => setImages(Array.from(e.target.files))} 
                    className="input" 
                    style={{ padding: '0.75rem' }}
                  />
                </div>
              )}
              
              <div>
                <label style={{ 
                  display: 'block', 
                  fontSize: '1.125rem', 
                  fontWeight: 600, 
                  marginBottom: '0.75rem',
                  color: 'var(--color-text-primary)'
                }}>
                  {labels.WHATSAPP_LABEL || 'WhatsApp (optional)'}
                </label>
                <input 
                  type="tel" 
                  value={form.whatsapp} 
                  onChange={e => setForm({...form, whatsapp: e.target.value})} 
                  className="input" 
                />
              </div>
              
              <div style={{ marginTop: '1rem' }}>
                <button 
                  type="submit" 
                  disabled={!devMode && !otpVerified} 
                  className="btn"
                  style={{ 
                    width: '100%',
                    opacity: (!devMode && !otpVerified) ? 0.5 : 1,
                    cursor: (!devMode && !otpVerified) ? 'not-allowed' : 'pointer'
                  }}
                >
                  {labels.POST_BUTTON || 'Post Ad'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
